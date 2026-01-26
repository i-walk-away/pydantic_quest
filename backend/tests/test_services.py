import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions.auth_exc import InvalidCredentials
from src.app.core.exceptions.base_exc import NotFoundError
from src.app.core.security.oauth_state import (
    build_code_challenge,
    create_oauth_state,
    parse_oauth_state,
)
from src.app.domain.models.db.user import User
from src.app.domain.models.dto.auth import LoginCredentials
from src.app.domain.models.dto.user import CreateUserDTO
from src.app.domain.models.enums.role import UserRole
from src.app.domain.repositories.user_repository import UserRepository
from src.app.domain.services.auth_service import AuthService
from src.app.domain.services.user_service import UserService


class FakeAuthManager:
    def __init__(self, *, verify_ok: bool = True) -> None:
        self.verify_ok = verify_ok

    def verify_password_against_hash(self, plain_password: str, hashed_password: str) -> bool:
        _ = plain_password
        _ = hashed_password
        return self.verify_ok

    @staticmethod
    def generate_jwt(input_data: dict, expires_in: int = 60) -> str:
        _ = input_data
        _ = expires_in
        return "token"


class FakeHashManager:
    @staticmethod
    def hash_password(password: str) -> str:
        _ = password
        return "hashed"


class FakeUserRepository:
    def __init__(self, user: User | None) -> None:
        self.user = user

    async def get_by_username(self, username: str) -> User | None:
        if self.user and self.user.username == username:
            return self.user
        return None


async def test_auth_service_login_success() -> None:
    user = User(username="alice", hashed_password="hashed", role=UserRole.USER)
    service = AuthService(
        user_repository=FakeUserRepository(user=user),
        auth_manager=FakeAuthManager(verify_ok=True),
    )

    token = await service.login(
        credentials=LoginCredentials(username="alice", plain_password="secret"),
    )

    assert token == "token"


async def test_auth_service_login_invalid_credentials() -> None:
    user = User(username="alice", hashed_password="hashed", role=UserRole.USER)
    service = AuthService(
        user_repository=FakeUserRepository(user=user),
        auth_manager=FakeAuthManager(verify_ok=False),
    )

    with pytest.raises(InvalidCredentials):
        await service.login(
            credentials=LoginCredentials(username="alice", plain_password="secret"),
        )


async def test_user_service_create_and_get(db_session: AsyncSession) -> None:
    repository = UserRepository(session=db_session)
    service = UserService(user_repository=repository, auth_manager=FakeHashManager())

    created = await service.create(
        schema=CreateUserDTO(username="user", plain_password="secret"),
    )
    fetched = await service.get_by_username(username="user")

    assert created.username == "user"
    assert fetched.username == "user"


async def test_user_service_get_missing(db_session: AsyncSession) -> None:
    repository = UserRepository(session=db_session)
    service = UserService(user_repository=repository, auth_manager=FakeHashManager())

    with pytest.raises(NotFoundError):
        await service.get_by_username(username="missing")


def test_oauth_state_roundtrip() -> None:
    state, code_verifier, cookie_value = create_oauth_state(secret="secret")

    parsed = parse_oauth_state(
        secret="secret",
        cookie_value=cookie_value,
        state=state,
    )

    assert parsed == code_verifier


def test_oauth_state_invalid_signature() -> None:
    state, _, cookie_value = create_oauth_state(secret="secret")
    parsed = parse_oauth_state(
        secret="wrong",
        cookie_value=cookie_value,
        state=state,
    )

    assert parsed is None


def test_code_challenge_deterministic() -> None:
    code_verifier = "verifier"
    first = build_code_challenge(code_verifier=code_verifier)
    second = build_code_challenge(code_verifier=code_verifier)

    assert first == second
