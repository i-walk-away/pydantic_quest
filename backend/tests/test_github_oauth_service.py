import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions.oauth_exc import (
    OAuthAccountConflict,
    OAuthConfigError,
    OAuthEmailNotVerifiedError,
    OAuthTokenExchangeError,
    OAuthTokenMissingError,
)
from src.app.domain.models.db.user import User
from src.app.domain.models.enums.role import UserRole
from src.app.domain.repositories.user_repository import UserRepository
from src.app.domain.services.github_oauth_service import GithubOAuthService
from src.cfg.cfg import settings


class FakeAuthManager:
    @staticmethod
    def generate_jwt(input_data: dict, expires_in: int = 60) -> str:
        _ = input_data
        _ = expires_in
        return "jwt-token"


class FakeResponse:
    def __init__(self, status_code: int, payload: object | None) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> object:
        if self._payload is None:
            message = "invalid json"
            raise ValueError(message)
        return self._payload


class FakeClient:
    def __init__(self, responses: dict[tuple[str, str], FakeResponse]) -> None:
        self.responses = responses

    async def post(self, url: str, *, data: dict, headers: dict) -> FakeResponse:
        _ = (data, headers)
        return self.responses[("POST", url)]

    async def get(self, url: str, *, headers: dict) -> FakeResponse:
        _ = headers
        return self.responses[("GET", url)]

    async def __aenter__(self) -> FakeClient:
        return self

    async def __aexit__(
            self,
            _exc_type: type[BaseException] | None,
            _exc: BaseException | None,
            _tb: object | None,
    ) -> None:
        return None


@pytest.fixture
def configured_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.github, "client_id", "client")
    monkeypatch.setattr(settings.github, "client_secret", "secret")
    monkeypatch.setattr(settings.github, "redirect_uri", "http://localhost/callback")
    monkeypatch.setattr(settings.github, "authorize_url", "https://github.com/authorize")
    monkeypatch.setattr(settings.github, "token_url", "https://github.com/token")
    monkeypatch.setattr(settings.github, "user_url", "https://api.github.com/user")
    monkeypatch.setattr(settings.github, "emails_url", "https://api.github.com/emails")
    monkeypatch.setattr(settings.github, "scope", "read:user user:email")
    monkeypatch.setattr(settings.github, "allow_signup", True)


def _install_fake_client(
        monkeypatch: pytest.MonkeyPatch,
        responses: dict[tuple[str, str], FakeResponse],
) -> None:
    monkeypatch.setattr(
        "src.app.domain.services.github_oauth_service.httpx.AsyncClient",
        lambda **_: FakeClient(responses),
    )


async def test_github_oauth_authenticate_success(
        configured_settings: None,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = configured_settings

    responses = {
        ("POST", settings.github.token_url): FakeResponse(
            status_code=200,
            payload={"access_token": "token"},
        ),
        ("GET", settings.github.user_url): FakeResponse(
            status_code=200,
            payload={"id": 123, "login": "octo"},
        ),
        ("GET", settings.github.emails_url): FakeResponse(
            status_code=200,
            payload=[{"email": "octo@example.com", "primary": True, "verified": True}],
        ),
    }
    _install_fake_client(monkeypatch, responses)

    repository = UserRepository(session=db_session)
    service = GithubOAuthService(user_repository=repository, auth_manager=FakeAuthManager())
    token = await service.authenticate(code="code", code_verifier="verifier")

    assert token == "jwt-token"
    created = await repository.get_by_github_id(github_id=123)
    assert created is not None
    assert created.username == "octo"


async def test_github_oauth_account_conflict(
        configured_settings: None,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = configured_settings

    existing = User(
        username="octo",
        email="octo@example.com",
        github_id=None,
        hashed_password=None,
        role=UserRole.USER,
    )
    db_session.add(existing)
    await db_session.commit()

    responses = {
        ("POST", settings.github.token_url): FakeResponse(
            status_code=200,
            payload={"access_token": "token"},
        ),
        ("GET", settings.github.user_url): FakeResponse(
            status_code=200,
            payload={"id": 999, "login": "octo"},
        ),
        ("GET", settings.github.emails_url): FakeResponse(
            status_code=200,
            payload=[{"email": "octo@example.com", "primary": True, "verified": True}],
        ),
    }
    _install_fake_client(monkeypatch, responses)

    repository = UserRepository(session=db_session)
    service = GithubOAuthService(user_repository=repository, auth_manager=FakeAuthManager())

    with pytest.raises(OAuthAccountConflict):
        await service.authenticate(code="code", code_verifier="verifier")


async def test_github_oauth_email_not_verified(
        configured_settings: None,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = configured_settings

    responses = {
        ("POST", settings.github.token_url): FakeResponse(
            status_code=200,
            payload={"access_token": "token"},
        ),
        ("GET", settings.github.user_url): FakeResponse(
            status_code=200,
            payload={"id": 456, "login": "octo"},
        ),
        ("GET", settings.github.emails_url): FakeResponse(
            status_code=200,
            payload=[{"email": "octo@example.com", "primary": True, "verified": False}],
        ),
    }
    _install_fake_client(monkeypatch, responses)

    repository = UserRepository(session=db_session)
    service = GithubOAuthService(user_repository=repository, auth_manager=FakeAuthManager())

    with pytest.raises(OAuthEmailNotVerifiedError):
        await service.authenticate(code="code", code_verifier="verifier")


@pytest.mark.parametrize(
    ("status_code", "payload", "expected_exc"),
    [
        (200, {"access_token": ""}, OAuthTokenMissingError),
        (400, {"error": "invalid"}, OAuthTokenExchangeError),
    ],
)
async def test_github_oauth_token_errors(
        configured_settings: None,
        db_session: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
        status_code: int,
        payload: dict,
        expected_exc: type[Exception],
) -> None:
    _ = configured_settings
    responses = {
        ("POST", settings.github.token_url): FakeResponse(
            status_code=status_code,
            payload=payload,
        ),
    }
    _install_fake_client(monkeypatch, responses)

    repository = UserRepository(session=db_session)
    service = GithubOAuthService(user_repository=repository, auth_manager=FakeAuthManager())

    with pytest.raises(expected_exc):
        await service.authenticate(code="code", code_verifier="verifier")


def test_github_oauth_missing_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.github, "client_id", None)
    monkeypatch.setattr(settings.github, "client_secret", None)
    monkeypatch.setattr(settings.github, "redirect_uri", None)

    with pytest.raises(OAuthConfigError):
        GithubOAuthService(
            user_repository=UserRepository(session=None),
            auth_manager=FakeAuthManager(),
        ).build_authorize_url(state="state", code_challenge="challenge")
