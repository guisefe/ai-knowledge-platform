from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.documents.models import DocumentVersion
from app.domain.documents.service import DocumentService, DocumentVersionService


class UnsupportedDocumentMediaTypeError(ValueError):
    pass


class DocumentTooLargeError(ValueError):
    pass


class InvalidDocumentContentError(ValueError):
    pass


class AsyncUploadSource(Protocol):
    async def read(self, size: int = -1) -> bytes: ...


@dataclass(frozen=True, slots=True)
class StagedDocument:
    staging_key: str
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    checksum_sha256: str


class DocumentStorage(Protocol):
    async def stage(
        self,
        source: AsyncUploadSource,
        *,
        filename: str | None,
        content_type: str | None,
    ) -> StagedDocument: ...

    async def promote(self, staged: StagedDocument, *, storage_key: str) -> None: ...

    async def discard(self, staged: StagedDocument) -> None: ...

    async def delete(self, storage_key: str) -> None: ...


@dataclass(frozen=True, slots=True)
class DocumentUploadResult:
    version: DocumentVersion
    created: bool


class DocumentUploadService:
    """Coordinate storage and database state as one upload use case."""

    def __init__(self, session: AsyncSession, storage: DocumentStorage) -> None:
        self._session = session
        self._storage = storage

    async def upload(
        self,
        source: AsyncUploadSource,
        *,
        owner_id: str,
        document_id: str,
        filename: str | None,
        content_type: str | None,
    ) -> DocumentUploadResult:
        # Reject foreign or deleted documents before accepting bytes into staging storage.
        await DocumentService(self._session).get(
            owner_id=owner_id,
            document_id=document_id,
        )
        staged = await self._storage.stage(
            source,
            filename=filename,
            content_type=content_type,
        )
        storage_key = self._storage_key(
            owner_id=owner_id,
            document_id=document_id,
            staged=staged,
        )
        promoted = False

        try:
            registration = await DocumentVersionService(self._session).register_version(
                owner_id=owner_id,
                document_id=document_id,
                original_filename=staged.original_filename,
                content_type=staged.content_type,
                size_bytes=staged.size_bytes,
                checksum_sha256=staged.checksum_sha256,
                storage_key=storage_key,
            )
            if registration.created:
                await self._storage.promote(staged, storage_key=storage_key)
                promoted = True

            await self._session.commit()
            return DocumentUploadResult(
                version=registration.version,
                created=registration.created,
            )
        except BaseException:
            await self._session.rollback()
            if promoted:
                await self._storage.delete(storage_key)
            raise
        finally:
            await self._storage.discard(staged)

    @staticmethod
    def _storage_key(
        *,
        owner_id: str,
        document_id: str,
        staged: StagedDocument,
    ) -> str:
        return str(
            PurePosixPath(
                "documents",
                owner_id,
                document_id,
                f"{staged.checksum_sha256}{staged.extension}",
            )
        )
