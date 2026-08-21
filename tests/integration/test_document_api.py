from uuid import uuid4

from httpx import AsyncClient


async def create_account_token(client: AsyncClient) -> str:
    email = f"document-owner-{uuid4().hex}@example.com"
    password = "a-secure-test-password"
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201

    token_response = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
    )
    assert token_response.status_code == 200
    return str(token_response.json()["access_token"])


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def create_document(client: AsyncClient, token: str, title: str) -> dict[str, object]:
    response = await client.post(
        "/api/v1/documents",
        headers=bearer(token),
        json={"title": title},
    )
    assert response.status_code == 201
    return response.json()


async def test_document_creation_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/documents",
        json={"title": "Operations policy"},
    )

    assert response.status_code == 401


async def test_create_normalizes_title_without_exposing_owner_id(client: AsyncClient) -> None:
    token = await create_account_token(client)

    response = await client.post(
        "/api/v1/documents",
        headers=bearer(token),
        json={"title": "  Operations policy  "},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Operations policy"
    assert "owner_id" not in response.json()


async def test_list_is_paginated_and_scoped_to_current_owner(client: AsyncClient) -> None:
    first_owner_token = await create_account_token(client)
    second_owner_token = await create_account_token(client)
    await create_document(client, first_owner_token, "First policy")
    await create_document(client, first_owner_token, "Second policy")
    await create_document(client, second_owner_token, "Foreign policy")

    response = await client.get(
        "/api/v1/documents",
        headers=bearer(first_owner_token),
        params={"limit": 1, "offset": 0},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 2
    assert payload["limit"] == 1
    assert payload["offset"] == 0
    assert len(payload["items"]) == 1
    assert payload["items"][0]["title"] != "Foreign policy"


async def test_get_does_not_reveal_another_owners_document(client: AsyncClient) -> None:
    owner_token = await create_account_token(client)
    another_owner_token = await create_account_token(client)
    document = await create_document(client, owner_token, "Restricted policy")

    foreign_response = await client.get(
        f"/api/v1/documents/{document['id']}",
        headers=bearer(another_owner_token),
    )
    foreign_delete_response = await client.delete(
        f"/api/v1/documents/{document['id']}",
        headers=bearer(another_owner_token),
    )
    missing_response = await client.get(
        f"/api/v1/documents/{uuid4()}",
        headers=bearer(another_owner_token),
    )
    owner_response = await client.get(
        f"/api/v1/documents/{document['id']}",
        headers=bearer(owner_token),
    )

    assert foreign_response.status_code == 404
    assert foreign_delete_response.status_code == 404
    assert foreign_response.json() == missing_response.json() == {"detail": "Document not found"}
    assert owner_response.status_code == 200


async def test_soft_delete_is_idempotent_and_hides_document(client: AsyncClient) -> None:
    token = await create_account_token(client)
    document = await create_document(client, token, "Obsolete policy")
    document_url = f"/api/v1/documents/{document['id']}"

    first_delete = await client.delete(document_url, headers=bearer(token))
    repeated_delete = await client.delete(document_url, headers=bearer(token))
    get_response = await client.get(document_url, headers=bearer(token))
    list_response = await client.get("/api/v1/documents", headers=bearer(token))

    assert first_delete.status_code == 204
    assert repeated_delete.status_code == 204
    assert get_response.status_code == 404
    assert list_response.json()["total"] == 0
