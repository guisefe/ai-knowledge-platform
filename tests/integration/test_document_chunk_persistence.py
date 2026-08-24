from hashlib import sha256
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.documents.models import Document, DocumentChunk, DocumentVersion
from app.domain.users.models import User
from app.infra.database import async_session_factory, engine


@pytest.fixture
async def db_session() -> AsyncSession:
    async with async_session_factory() as session:
        transaction = await session.begin()
        try:
            yield session
        finally:
            await transaction.rollback()
    await engine.dispose()


async def create_version(session: AsyncSession) -> DocumentVersion:
    suffix = uuid4().hex
    owner = User(
        email=f"chunk-owner-{suffix}@example.com",
        hashed_password="not-used-by-this-test",
    )
    session.add(owner)
    await session.flush()

    document = Document(owner_id=owner.id, title="Operations policy")
    session.add(document)
    await session.flush()

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        original_filename="operations-policy.md",
        content_type="text/markdown",
        size_bytes=64,
        checksum_sha256=sha256(suffix.encode()).hexdigest(),
        storage_key=f"documents/{owner.id}/{document.id}/{suffix}.md",
    )
    session.add(version)
    await session.flush()
    return version


def make_chunk(
    version: DocumentVersion,
    *,
    position: int,
    source: str,
    start_offset: int,
    end_offset: int,
) -> DocumentChunk:
    content = source[start_offset:end_offset]
    return DocumentChunk(
        document_version_id=version.id,
        position=position,
        content=content,
        content_sha256=sha256(content.encode()).hexdigest(),
        start_offset=start_offset,
        end_offset=end_offset,
    )


async def test_chunks_persist_order_and_source_provenance(db_session: AsyncSession) -> None:
    version = await create_version(db_session)
    source = "Cancellation requires review.\nBilling must approve the request."
    second_start = source.index("Billing")
    chunks = [
        make_chunk(
            version,
            position=1,
            source=source,
            start_offset=second_start,
            end_offset=len(source),
        ),
        make_chunk(
            version,
            position=0,
            source=source,
            start_offset=0,
            end_offset=second_start - 1,
        ),
    ]
    db_session.add_all(chunks)
    await db_session.flush()

    stored = list(
        (
            await db_session.scalars(
                select(DocumentChunk)
                .where(DocumentChunk.document_version_id == version.id)
                .order_by(DocumentChunk.position)
            )
        ).all()
    )

    assert [chunk.position for chunk in stored] == [0, 1]
    for chunk in stored:
        assert chunk.content == source[chunk.start_offset : chunk.end_offset]
        assert chunk.content_sha256 == sha256(chunk.content.encode()).hexdigest()


async def test_duplicate_chunk_position_is_rejected(db_session: AsyncSession) -> None:
    version = await create_version(db_session)
    source = "One deterministic passage."
    first = make_chunk(
        version,
        position=0,
        source=source,
        start_offset=0,
        end_offset=len(source),
    )
    db_session.add(first)
    await db_session.flush()

    duplicate = make_chunk(
        version,
        position=0,
        source=source,
        start_offset=0,
        end_offset=len(source),
    )

    with pytest.raises(IntegrityError):
        async with db_session.begin_nested():
            db_session.add(duplicate)
            await db_session.flush()
