from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import InvalidAccessTokenError, decode_access_token
from app.domain.users.models import User
from app.infra.database import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]
BearerToken = Annotated[str, Depends(oauth2_scheme)]


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: BearerToken, session: DatabaseSession) -> User:
    try:
        claims = decode_access_token(token)
    except InvalidAccessTokenError as exc:
        raise _unauthorized() from exc

    user = await session.get(User, claims.subject)
    if user is None or not user.is_active:
        raise _unauthorized()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
