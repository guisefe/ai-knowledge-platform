from datetime import UTC, datetime, timedelta

import pytest

from app.core.config import Settings
from app.core.security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_is_hashed_with_argon2() -> None:
    encoded = hash_password("correct horse battery staple")

    assert encoded != "correct horse battery staple"
    assert encoded.startswith("$argon2")
    assert verify_password("correct horse battery staple", encoded) is True
    assert verify_password("wrong password", encoded) is False


def test_access_token_round_trip_preserves_required_claims() -> None:
    issued_at = datetime.now(UTC).replace(microsecond=0)

    token = create_access_token("user-123", now=issued_at)
    claims = decode_access_token(token)

    assert claims.subject == "user-123"
    assert claims.issued_at == issued_at
    assert claims.expires_at > claims.issued_at
    assert claims.token_id


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(
        "user-123",
        now=datetime.now(UTC) - timedelta(hours=2),
        expires_delta=timedelta(minutes=1),
    )

    with pytest.raises(InvalidAccessTokenError, match="invalid or expired"):
        decode_access_token(token)


def test_tampered_access_token_is_rejected() -> None:
    token = create_access_token("user-123")
    replacement = "a" if token[-1] != "a" else "b"

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(f"{token[:-1]}{replacement}")


def test_production_rejects_default_jwt_secret() -> None:
    with pytest.raises(ValueError, match="at least 32 characters"):
        Settings(APP_ENV="production", JWT_SECRET_KEY="change-me", _env_file=None)
