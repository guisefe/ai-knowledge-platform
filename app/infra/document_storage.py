import asyncio
import codecs
import hashlib
import os
from functools import lru_cache
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.core.config import settings
from app.domain.documents.upload import (
    AsyncUploadSource,
    DocumentStorage,
    DocumentTooLargeError,
    InvalidDocumentContentError,
    StagedDocument,
    UnsupportedDocumentMediaTypeError,
)

_CHUNK_SIZE = 64 * 1024
_ALLOWED_MEDIA_TYPES = {
    ".md": {"text/markdown", "text/plain"},
    ".txt": {"text/plain"},
}


class LocalDocumentStorage:
    """Store validated document content with atomic local-file promotion."""

    def __init__(self, root: Path, *, max_size_bytes: int) -> None:
        self._root = root.resolve()
        self._staging_root = self._root / ".staging"
        self._max_size_bytes = max_size_bytes

    async def stage(
        self,
        source: AsyncUploadSource,
        *,
        filename: str | None,
        content_type: str | None,
    ) -> StagedDocument:
        safe_filename, extension, normalized_content_type = self._validate_metadata(
            filename=filename,
            content_type=content_type,
        )
        await asyncio.to_thread(self._staging_root.mkdir, parents=True, exist_ok=True)
        staging_key = uuid4().hex
        staging_path = self._staging_root / staging_key
        handle = await asyncio.to_thread(staging_path.open, "xb")
        checksum = hashlib.sha256()
        decoder = codecs.getincrementaldecoder("utf-8")()
        size_bytes = 0

        try:
            while chunk := await source.read(_CHUNK_SIZE):
                size_bytes += len(chunk)
                if size_bytes > self._max_size_bytes:
                    raise DocumentTooLargeError(
                        f"Document exceeds the {self._max_size_bytes}-byte limit"
                    )

                try:
                    decoded = decoder.decode(chunk)
                except UnicodeDecodeError as exc:
                    raise InvalidDocumentContentError(
                        "Document content must be valid UTF-8 text"
                    ) from exc
                if "\x00" in decoded:
                    raise InvalidDocumentContentError("Document content cannot contain null bytes")

                checksum.update(chunk)
                await asyncio.to_thread(handle.write, chunk)

            try:
                decoder.decode(b"", final=True)
            except UnicodeDecodeError as exc:
                raise InvalidDocumentContentError(
                    "Document content must be valid UTF-8 text"
                ) from exc
            if size_bytes == 0:
                raise InvalidDocumentContentError("Document content cannot be empty")

            await asyncio.to_thread(self._flush_and_sync, handle)
        except BaseException:
            await asyncio.to_thread(handle.close)
            await asyncio.to_thread(staging_path.unlink, missing_ok=True)
            raise
        else:
            await asyncio.to_thread(handle.close)

        return StagedDocument(
            staging_key=staging_key,
            original_filename=safe_filename,
            content_type=normalized_content_type,
            extension=extension,
            size_bytes=size_bytes,
            checksum_sha256=checksum.hexdigest(),
        )

    async def promote(self, staged: StagedDocument, *, storage_key: str) -> None:
        source_path = self._staging_root / staged.staging_key
        target_path = self._safe_target(storage_key)
        await asyncio.to_thread(target_path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(os.replace, source_path, target_path)

    async def discard(self, staged: StagedDocument) -> None:
        staging_path = self._staging_root / staged.staging_key
        await asyncio.to_thread(staging_path.unlink, missing_ok=True)

    async def delete(self, storage_key: str) -> None:
        await asyncio.to_thread(self._safe_target(storage_key).unlink, missing_ok=True)

    def _safe_target(self, storage_key: str) -> Path:
        target_path = (self._root / storage_key).resolve()
        if not target_path.is_relative_to(self._root):
            raise ValueError("Storage key escapes the configured document root")
        return target_path

    @staticmethod
    def _validate_metadata(
        *,
        filename: str | None,
        content_type: str | None,
    ) -> tuple[str, str, str]:
        safe_filename = (filename or "").replace("\\", "/").rsplit("/", maxsplit=1)[-1]
        if not safe_filename or len(safe_filename) > 255:
            raise UnsupportedDocumentMediaTypeError("A valid filename is required")

        extension = Path(safe_filename).suffix.lower()
        normalized_content_type = (content_type or "").split(";", maxsplit=1)[0].strip().lower()
        if normalized_content_type not in _ALLOWED_MEDIA_TYPES.get(extension, set()):
            raise UnsupportedDocumentMediaTypeError(
                "Only UTF-8 .txt and .md documents are supported"
            )
        return safe_filename, extension, normalized_content_type

    @staticmethod
    def _flush_and_sync(handle: BinaryIO) -> None:
        handle.flush()
        os.fsync(handle.fileno())


@lru_cache
def get_document_storage() -> DocumentStorage:
    return LocalDocumentStorage(
        settings.DOCUMENT_STORAGE_ROOT,
        max_size_bytes=settings.MAX_DOCUMENT_SIZE_BYTES,
    )
