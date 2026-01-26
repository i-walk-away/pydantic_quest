import httpx

from main import app
from src.app.core.dependencies.services.auth import get_auth_service
from src.app.core.exceptions.auth_exc import InvalidCredentials


class FakeAuthService:
    def __init__(self, token: str, *, allow: bool = True) -> None:
        self.token = token
        self.allow = allow

    async def login(self, *, credentials: object) -> str:
        _ = credentials
        if not self.allow:
            raise InvalidCredentials
        return self.token


async def test_login_success(
        client: httpx.AsyncClient,
) -> None:
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService(token="token")

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "plain_password": "secret"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

    app.dependency_overrides.pop(get_auth_service, None)


async def test_login_invalid_password(
        client: httpx.AsyncClient,
) -> None:
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService(
        token="token",
        allow=False,
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "bob", "plain_password": "wrong"},
    )

    assert response.status_code == 401

    app.dependency_overrides.pop(get_auth_service, None)
