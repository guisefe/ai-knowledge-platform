from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.domain.users.models import User


class EmailAlreadyRegisteredError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


# Verifying a real hash when the account does not exist reduces email-enumeration timing leaks.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-used-only-for-timing-safety")


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register(self, *, email: str, password: str) -> User:
        normalized_email = self._normalize_email(email)
        existing_user = await self._session.scalar(
            select(User.id).where(User.email == normalized_email)
        )
        if existing_user is not None:
            raise EmailAlreadyRegisteredError("Email is already registered")

        user = User(
            email=normalized_email,
            hashed_password=hash_password(password),
        )

        try:
            async with self._session.begin_nested():
                self._session.add(user)
                await self._session.flush()
        except IntegrityError as exc:
            # The unique index remains authoritative under concurrent registrations.
            raise EmailAlreadyRegisteredError("Email is already registered") from exc

        return user

    async def authenticate(self, *, email: str, password: str) -> User:
        normalized_email = self._normalize_email(email)
        user = await self._session.scalar(select(User).where(User.email == normalized_email))
        encoded_password = user.hashed_password if user is not None else _DUMMY_PASSWORD_HASH
        password_matches = verify_password(password, encoded_password)

        if user is None or not password_matches or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password")

        return user

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().casefold()
