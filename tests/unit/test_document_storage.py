import hashlib
from io import BytesIO
from pathlib import Path

import pytest

from app.domain.documents.upload import (
    DocumentTooLargeError,
    InvalidDocumentContentError,
)
from app.infra.document_storage import LocalDocumentStorage


class MemoryUpload:
    def __init__(self, content: bytes) -> None:
        self._stream = BytesIO(content)

    async def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)


async def test_stage_and_promote_valid_utf8_document(tmp_path: Path) -> None:
    content = "Política operacional".encode()
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)

    staged = await storage.stage(
        MemoryUpload(content),
        filename="../../policy.md",
        content_type="text/markdown; charset=utf-8",
    )
    storage_key = f"documents/owner/document/{staged.checksum_sha256}.md"
    await storage.promote(staged, storage_key=storage_key)

    assert staged.original_filename == "policy.md"
    assert staged.size_bytes == len(content)
    assert staged.checksum_sha256 == hashlib.sha256(content).hexdigest()
    assert (tmp_path / storage_key).read_bytes() == content


async def test_oversized_document_is_removed_from_staging(tmp_path: Path) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=4)

    with pytest.raises(DocumentTooLargeError):
        await storage.stage(
            MemoryUpload(b"12345"),
            filename="policy.txt",
            content_type="text/plain",
        )

    assert list((tmp_path / ".staging").iterdir()) == []


async def test_storage_key_cannot_escape_configured_root(tmp_path: Path) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)
    staged = await storage.stage(
        MemoryUpload(b"safe content"),
        filename="policy.txt",
        content_type="text/plain",
    )

    with pytest.raises(ValueError, match="escapes"):
        await storage.promote(staged, storage_key="../outside.txt")

    await storage.discard(staged)
    assert not (tmp_path.parent / "outside.txt").exists()


@pytest.mark.parametrize("content", [b"", b"\xff\xfe", b"text\x00content"])
async def test_invalid_text_content_is_rejected(tmp_path: Path, content: bytes) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)

    with pytest.raises(InvalidDocumentContentError):
        await storage.stage(
            MemoryUpload(content),
            filename="policy.txt",
            content_type="text/plain",
        )
