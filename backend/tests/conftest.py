from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from pathlib import Path

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

TEST_ENV_DEFAULTS = {
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_NAME": "pydanticquest_test",
    "DB_USERNAME": "test",
    "DB_PASSWORD": "test",
    "JWT_SECRET_KEY": "test-secret",
    "JWT_ALGORITHM": "HS256",
    "JWT_LIFESPAN": "50",
    "FRONTEND_URL": "http://localhost:5173",
    "GITHUB_CLIENT_ID": "test",
    "GITHUB_CLIENT_SECRET": "test",
    "GITHUB_REDIRECT_URI": "http://localhost:8000/api/v1/auth/github/callback",
    "GITHUB_SCOPE": "read:user user:email",
    "GITHUB_ALLOW_SIGNUP": "true",
    "GITHUB_AUTHORIZE_URL": "https://github.com/login/oauth/authorize",
    "GITHUB_TOKEN_URL": "https://github.com/login/oauth/access_token",
    "GITHUB_USER_URL": "https://api.github.com/user",
    "GITHUB_EMAILS_URL": "https://api.github.com/user/emails",
    "PISTON_URL": "http://localhost:2000",
    "PISTON_LANGUAGE": "python",
    "PISTON_VERSION": "3.12",
    "PISTON_RUN_TIMEOUT_MS": "10000",
    "PISTON_COMPILE_TIMEOUT_MS": "10000",
    "PISTON_RUN_MEMORY_LIMIT_BYTES": "134217728",
    "PISTON_COMPILE_MEMORY_LIMIT_BYTES": "134217728",
    "EXECUTION_MAX_OUTPUT_CHARS": "16000",
    "EXECUTION_MAX_USER_CODE_CHARS": "20000",
    "EXECUTION_MAX_EVAL_SCRIPT_CHARS": "60000",
    "EXECUTION_MAX_SOURCE_CHARS": "80000",
    "PISTON_MAX_RETRIES": "2",
    "PISTON_RETRY_DELAY_MS": "200",
    "PISTON_HEALTH_TTL_SEC": "30",
    "PISTON_HTTP_TIMEOUT_MS": "5000",
    "EXECUTION_RATE_LIMIT_WINDOW_SEC": "60",
    "EXECUTION_RATE_LIMIT_MAX": "20",
    "LESSONS_DIR": str(Path(__file__).resolve().parents[2] / "lessons"),
}

for key, value in TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(key=key, value=value)

from main import app
from src.app.core.dependencies.db import get_session
from src.app.core.dependencies.security.crypt_context import get_crypt_context
from src.app.core.dependencies.services.execution_rate_limiter import (
    get_execution_rate_limiter,
)
from src.app.core.security.auth_manager import AuthManager
from src.app.domain.models.db import Base
from src.app.domain.models.db.user import User
from src.app.domain.models.enums.role import UserRole
from src.app.domain.services.execution_rate_limiter import ExecutionRateLimiter


@pytest.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def session_factory(
        async_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(
        session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        await session.execute(text("DELETE FROM lesson_progress"))
        await session.execute(text("DELETE FROM lessons"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
        yield session


@pytest.fixture
def auth_manager() -> AuthManager:
    return AuthManager(context=get_crypt_context())


@pytest.fixture
def user_factory(
        db_session: AsyncSession,
) -> Callable[[str, str, UserRole], Awaitable[User]]:
    async def _create_user(username: str, _password: str, role: UserRole) -> User:
        user = User(
            username=username,
            hashed_password="hashed",
            role=role,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        return user

    return _create_user


@pytest.fixture
async def admin_headers(
        user_factory: Callable[[str, str, UserRole], Awaitable[User]],
        auth_manager: AuthManager,
) -> dict[str, str]:
    user = await user_factory("admin", "secret", UserRole.ADMIN)
    token = auth_manager.generate_jwt(
        input_data={
            "sub": user.username,
            "role": user.role.value,
        },
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def user_headers(
        user_factory: Callable[[str, str, UserRole], Awaitable[User]],
        auth_manager: AuthManager,
) -> dict[str, str]:
    user = await user_factory("user", "secret", UserRole.USER)
    token = auth_manager.generate_jwt(
        input_data={
            "sub": user.username,
            "role": user.role.value,
        },
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client(
        session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[httpx.AsyncClient]:
    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session

    async with session_factory() as session:
        await session.execute(text("DELETE FROM lesson_progress"))
        await session.execute(text("DELETE FROM lessons"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()

    app.dependency_overrides[get_session] = override_get_session
    rate_limiter = ExecutionRateLimiter(max_requests=100, window_sec=60)
    app.dependency_overrides[get_execution_rate_limiter] = lambda: rate_limiter

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()
