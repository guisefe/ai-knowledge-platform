from uuid import uuid4

import pytest
from httpx import AsyncClient


def unique_email() -> str:
    return f"user-{uuid4().hex}@example.com"


async def register(client: AsyncClient, email: str, password: str) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201


async def test_registration_normalizes_email_and_hides_password(client: AsyncClient) -> None:
    email = unique_email()

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email.upper(), "password": "a-secure-test-password"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


async def test_duplicate_registration_returns_conflict(client: AsyncClient) -> None:
    email = unique_email()
    password = "a-secure-test-password"
    await register(client, email, password)

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email.upper(), "password": password},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email is already registered"}


async def test_login_token_identifies_current_user(client: AsyncClient) -> None:
    email = unique_email()
    password = "a-secure-test-password"
    await register(client, email, password)

    token_response = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    token_payload = token_response.json()
    current_user_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_payload['access_token']}"},
    )

    assert token_response.status_code == 200
    assert token_payload["token_type"] == "bearer"
    assert token_payload["expires_in"] == 3600
    assert current_user_response.status_code == 200
    assert current_user_response.json()["email"] == email


async def test_wrong_password_returns_bearer_challenge(client: AsyncClient) -> None:
    email = unique_email()
    await register(client, email, "a-secure-test-password")

    response = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "the-wrong-password"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-token"},
    ],
)
async def test_me_rejects_missing_or_invalid_token(
    client: AsyncClient,
    headers: dict[str, str],
) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
