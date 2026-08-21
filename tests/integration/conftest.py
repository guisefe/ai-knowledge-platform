from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.infra.database import engine
from app.infra.document_storage import LocalDocumentStorage, get_document_storage
from app.main import app


@pytest.fixture
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)
    app.dependency_overrides[get_document_storage] = lambda: storage

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_document_storage, None)
        await engine.dispose()
