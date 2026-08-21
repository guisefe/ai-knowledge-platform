import asyncio
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient, Response


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


async def create_document(client: AsyncClient, token: str, title: str) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/documents",
        headers=bearer(token),
        json={"title": title},
    )
    assert response.status_code == 201
    return response.json()


async def upload_version(
    client: AsyncClient,
    token: str,
    document_id: str,
    content: bytes,
    *,
    filename: str = "policy.md",
    content_type: str = "text/markdown",
) -> Response:
    return await client.post(
        f"/api/v1/documents/{document_id}/versions",
        headers=bearer(token),
        files={"file": (filename, content, content_type)},
    )


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


async def test_upload_is_idempotent_and_changed_content_creates_next_version(
    client: AsyncClient,
) -> None:
    token = await create_account_token(client)
    document = await create_document(client, token, "Versioned policy")

    first = await upload_version(client, token, document["id"], b"first policy content")
    duplicate = await upload_version(client, token, document["id"], b"first policy content")
    changed = await upload_version(client, token, document["id"], b"revised policy content")

    assert first.status_code == 201
    assert first.json()["created"] is True
    assert first.json()["version_number"] == 1
    assert "storage_key" not in first.json()
    assert duplicate.status_code == 200
    assert duplicate.json()["created"] is False
    assert duplicate.json()["id"] == first.json()["id"]
    assert changed.status_code == 201
    assert changed.json()["version_number"] == 2


async def test_concurrent_identical_uploads_create_one_version(client: AsyncClient) -> None:
    token = await create_account_token(client)
    document = await create_document(client, token, "Concurrent policy")

    responses = await asyncio.gather(
        upload_version(client, token, document["id"], b"same concurrent content"),
        upload_version(client, token, document["id"], b"same concurrent content"),
    )

    assert sorted(response.status_code for response in responses) == [200, 201]
    assert responses[0].json()["id"] == responses[1].json()["id"]


@pytest.mark.parametrize(
    ("filename", "content", "content_type", "expected_status"),
    [
        ("policy.pdf", b"not a pdf", "application/pdf", 415),
        ("policy.txt", b"\xff\xfe", "text/plain", 422),
        ("policy.md", b"x" * 1025, "text/markdown", 413),
    ],
)
async def test_upload_rejects_unsupported_invalid_or_oversized_content(
    client: AsyncClient,
    filename: str,
    content: bytes,
    content_type: str,
    expected_status: int,
) -> None:
    token = await create_account_token(client)
    document = await create_document(client, token, "Validated policy")

    response = await upload_version(
        client,
        token,
        document["id"],
        content,
        filename=filename,
        content_type=content_type,
    )

    assert response.status_code == expected_status


async def test_upload_does_not_reveal_or_store_for_foreign_document(
    client: AsyncClient,
) -> None:
    owner_token = await create_account_token(client)
    another_owner_token = await create_account_token(client)
    document = await create_document(client, owner_token, "Private policy")

    response = await upload_version(
        client,
        another_owner_token,
        document["id"],
        b"foreign content",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
