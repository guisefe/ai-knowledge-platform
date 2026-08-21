from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.documents.models import Document, DocumentVersion, DocumentVersionStatus
from app.domain.documents.service import (
    DocumentNotFoundError,
    DocumentVersionService,
    VersionRegistration,
)
from app.domain.users.models import User
from app.infra.database import async_session_factory


@pytest.fixture
async def db_session() -> AsyncSession:
    async with async_session_factory() as session:
        transaction = await session.begin()
        try:
            yield session
        finally:
            await transaction.rollback()


async def create_document(session: AsyncSession) -> tuple[User, Document]:
    suffix = uuid4().hex
    owner = User(
        email=f"owner-{suffix}@example.com",
        hashed_password="not-used-by-this-test",
    )
    session.add(owner)
    await session.flush()

    document = Document(owner_id=owner.id, title="Operations policy")
    session.add(document)
    await session.flush()
    return owner, document


async def register_version(
    service: DocumentVersionService,
    *,
    owner_id: str,
    document_id: str,
    checksum: str,
    storage_suffix: str,
) -> VersionRegistration:
    return await service.register_version(
        owner_id=owner_id,
        document_id=document_id,
        original_filename="operations-policy.md",
        content_type="text/markdown",
        size_bytes=1024,
        checksum_sha256=checksum,
        storage_key=f"documents/{owner_id}/{document_id}/{storage_suffix}.md",
    )


async def test_first_upload_creates_version_one(db_session: AsyncSession) -> None:
    owner, document = await create_document(db_session)
    service = DocumentVersionService(db_session)

    result = await register_version(
        service,
        owner_id=owner.id,
        document_id=document.id,
        checksum="a" * 64,
        storage_suffix="1",
    )

    assert result.created is True
    assert result.version.version_number == 1
    assert result.version.status is DocumentVersionStatus.UPLOADED


async def test_identical_content_returns_existing_version(db_session: AsyncSession) -> None:
    owner, document = await create_document(db_session)
    service = DocumentVersionService(db_session)

    first = await register_version(
        service,
        owner_id=owner.id,
        document_id=document.id,
        checksum="b" * 64,
        storage_suffix="1",
    )
    duplicate = await register_version(
        service,
        owner_id=owner.id,
        document_id=document.id,
        checksum="b" * 64,
        storage_suffix="duplicate",
    )
    stored_versions = await db_session.scalar(
        select(func.count(DocumentVersion.id)).where(DocumentVersion.document_id == document.id)
    )

    assert duplicate.created is False
    assert duplicate.version.id == first.version.id
    assert stored_versions == 1


async def test_changed_content_increments_version_number(db_session: AsyncSession) -> None:
    owner, document = await create_document(db_session)
    service = DocumentVersionService(db_session)

    await register_version(
        service,
        owner_id=owner.id,
        document_id=document.id,
        checksum="c" * 64,
        storage_suffix="1",
    )
    changed = await register_version(
        service,
        owner_id=owner.id,
        document_id=document.id,
        checksum="d" * 64,
        storage_suffix="2",
    )

    assert changed.created is True
    assert changed.version.version_number == 2


async def test_owner_scope_does_not_reveal_foreign_document(db_session: AsyncSession) -> None:
    _, document = await create_document(db_session)
    service = DocumentVersionService(db_session)

    with pytest.raises(DocumentNotFoundError, match="ownership scope"):
        await register_version(
            service,
            owner_id="another-owner",
            document_id=document.id,
            checksum="e" * 64,
            storage_suffix="1",
        )


async def test_soft_deleted_document_rejects_new_versions(db_session: AsyncSession) -> None:
    owner, document = await create_document(db_session)
    document.soft_delete()
    await db_session.flush()
    service = DocumentVersionService(db_session)

    with pytest.raises(DocumentNotFoundError):
        await register_version(
            service,
            owner_id=owner.id,
            document_id=document.id,
            checksum="f" * 64,
            storage_suffix="1",
        )
