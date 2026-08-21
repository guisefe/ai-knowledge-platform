from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_endpoint_contract() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_root_endpoint_contract() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == "AI Knowledge Backend"
    assert payload["status"] == "running"
    assert payload["docs"] == "/docs"
    assert payload["health"] == "/api/v1/health"
