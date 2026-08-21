from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.infra.database import engine
from app.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client
    await engine.dispose()
