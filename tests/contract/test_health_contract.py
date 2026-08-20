from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_contract() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint_contract() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == "AI Knowledge Backend"
    assert payload["status"] == "running"
    assert payload["docs"] == "/docs"
    assert payload["health"] == "/api/v1/health"
