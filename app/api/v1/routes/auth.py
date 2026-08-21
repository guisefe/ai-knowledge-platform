from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.config import settings
from app.core.security import create_access_token
from app.domain.users.schemas import AccessTokenResponse, UserRegistration, UserResponse
from app.domain.users.service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserService,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(payload: UserRegistration, session: DatabaseSession) -> UserResponse:
    service = UserService(session)

    try:
        user = await service.register(email=str(payload.email), password=payload.password)
        await session.commit()
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserResponse.model_validate(user)


@router.post("/token", response_model=AccessTokenResponse)
async def issue_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DatabaseSession,
) -> AccessTokenResponse:
    service = UserService(session)

    try:
        user = await service.authenticate(email=form.username, password=form.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return AccessTokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
