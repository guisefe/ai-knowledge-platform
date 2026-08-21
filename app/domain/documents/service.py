from dataclasses import dataclass
from re import fullmatch

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.documents.models import Document, DocumentVersion


class DocumentNotFoundError(LookupError):
    pass


@dataclass(frozen=True, slots=True)
class VersionRegistration:
    version: DocumentVersion
    created: bool


class DocumentVersionService:
    """Register versions inside a transaction owned by the caller."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register_version(
        self,
        *,
        owner_id: str,
        document_id: str,
        original_filename: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
        storage_key: str,
    ) -> VersionRegistration:
        self._validate_content_metadata(
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
        )

        document = await self._session.scalar(
            select(Document)
            .where(
                Document.id == document_id,
                Document.owner_id == owner_id,
                Document.deleted_at.is_(None),
            )
            .with_for_update()
        )
        if document is None:
            # A shared error avoids revealing whether a document belongs to another owner.
            raise DocumentNotFoundError("Document was not found in the current ownership scope")

        existing_version = await self._session.scalar(
            select(DocumentVersion).where(
                DocumentVersion.document_id == document.id,
                DocumentVersion.checksum_sha256 == checksum_sha256,
            )
        )
        if existing_version is not None:
            return VersionRegistration(version=existing_version, created=False)

        latest_version_number = await self._session.scalar(
            select(func.max(DocumentVersion.version_number)).where(
                DocumentVersion.document_id == document.id
            )
        )
        version = DocumentVersion(
            document_id=document.id,
            version_number=(latest_version_number or 0) + 1,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
            storage_key=storage_key,
        )
        self._session.add(version)
        await self._session.flush()

        return VersionRegistration(version=version, created=True)

    @staticmethod
    def _validate_content_metadata(*, size_bytes: int, checksum_sha256: str) -> None:
        if size_bytes < 0:
            raise ValueError("Document size cannot be negative")
        if fullmatch(r"[0-9a-f]{64}", checksum_sha256) is None:
            raise ValueError("Document checksum must be a lowercase SHA-256 digest")
