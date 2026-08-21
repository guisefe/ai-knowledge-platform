from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


class InvalidAccessTokenError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    subject: str
    issued_at: datetime
    expires_at: datetime
    token_id: str


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return password_hash.hash(password)


def verify_password(password: str, encoded_password: str) -> bool:
    if not password or not encoded_password:
        return False
    return password_hash.verify(password, encoded_password)


def create_access_token(
    subject: str,
    *,
    now: datetime | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    if not subject:
        raise ValueError("Access token subject cannot be empty")

    issued_at = now or datetime.now(UTC)
    if issued_at.tzinfo is None:
        raise ValueError("Access token timestamps must be timezone-aware")

    lifetime = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if lifetime <= timedelta(0):
        raise ValueError("Access token lifetime must be positive")

    payload = {
        "sub": subject,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": issued_at + lifetime,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> AccessTokenClaims:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"require": ["sub", "iss", "aud", "iat", "nbf", "exp", "jti"]},
        )
        return AccessTokenClaims(
            subject=payload["sub"],
            issued_at=datetime.fromtimestamp(payload["iat"], UTC),
            expires_at=datetime.fromtimestamp(payload["exp"], UTC),
            token_id=payload["jti"],
        )
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise InvalidAccessTokenError("Access token is invalid or expired") from exc
