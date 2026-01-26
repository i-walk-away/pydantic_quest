from uuid import uuid4

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jwt import encode

from src.app.core.dependencies.security.user import get_user_from_jwt, require_admin_user
from src.app.core.exceptions.auth_exc import InvalidCredentials, Unauthorized
from src.app.core.exceptions.base_exc import NotFoundError
from src.app.domain.models.dto.user import UserDTO
from src.app.domain.models.enums.role import UserRole
from src.cfg.cfg import settings


class FakeUserService:
    def __init__(self, user: UserDTO | None, *, raise_missing: bool = False) -> None:
        self.user = user
        self.raise_missing = raise_missing

    async def get_by_username(self, username: str) -> UserDTO:
        if self.raise_missing:
            raise NotFoundError(
                entity_type_str="User",
                field_name="username",
                field_value=username,
            )
        if self.user and self.user.username == username:
            return self.user
        raise NotFoundError(
            entity_type_str="User",
            field_name="username",
            field_value=username,
        )


def _build_token(username: str) -> str:
    return encode(
        payload={"sub": username},
        key=settings.auth.jwt_secret_key,
        algorithm=settings.auth.jwt_algorithm,
    )


async def test_get_user_from_jwt_success() -> None:
    user = UserDTO(
        id=uuid4(),
        username="alice",
        email=None,
        role=UserRole.USER,
    )
    token = _build_token(username="alice")
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    result = await get_user_from_jwt(
        user_service=FakeUserService(user=user),
        jwt=creds,
    )

    assert result.username == "alice"


async def test_get_user_from_jwt_missing_user() -> None:
    token = _build_token(username="missing")
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(InvalidCredentials):
        await get_user_from_jwt(
            user_service=FakeUserService(user=None, raise_missing=True),
            jwt=creds,
        )


async def test_get_user_from_jwt_invalid_token() -> None:
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")

    with pytest.raises(InvalidCredentials):
        await get_user_from_jwt(
            user_service=FakeUserService(user=None),
            jwt=creds,
        )


async def test_require_admin_user_denied() -> None:
    user = UserDTO(
        id=uuid4(),
        username="bob",
        email=None,
        role=UserRole.USER,
    )

    with pytest.raises(Unauthorized):
        await require_admin_user(user=user)
