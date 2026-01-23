from urllib.parse import urlencode

import httpx

from src.app.core.exceptions.oauth_exc import (
    OAuthAccountConflict,
    OAuthConfigError,
    OAuthEmailFetchError,
    OAuthEmailNotVerifiedError,
    OAuthTokenExchangeError,
    OAuthTokenMissingError,
    OAuthUserFetchError,
)
from src.app.core.security.auth_manager import AuthManager
from src.app.domain.models.db.user import User
from src.app.domain.models.dto.auth import GithubEmailDTO, GithubTokenDTO, GithubUserDTO
from src.app.domain.models.enums.role import UserRole
from src.app.domain.repositories import UserRepository
from src.cfg.cfg import settings


class GithubOAuthService:
    """
    Handles GitHub OAuth authentication flow.
    """

    def __init__(self, user_repository: UserRepository, auth_manager: AuthManager) -> None:
        """
        Initialize GitHub OAuth service.

        :param user_repository: user repository
        :param auth_manager: auth manager

        :return: None
        """
        self.user_repository = user_repository
        self.auth_manager = auth_manager

    def build_authorize_url(self, state: str, code_challenge: str) -> str:
        """
        Build GitHub authorization URL.

        :param state: OAuth state
        :param code_challenge: PKCE code challenge

        :return: GitHub authorization URL
        """
        self._ensure_configured()

        params = self._build_authorize_params(
            state=state,
            code_challenge=code_challenge,
        )

        return f"{settings.github.authorize_url}?{urlencode(params)}"

    async def authenticate(self, code: str, code_verifier: str) -> str:
        """
        Authenticate user via GitHub OAuth code exchange.

        :param code: authorization code
        :param code_verifier: PKCE code verifier

        :return: JSON Web Token
        """
        self._ensure_configured()

        token = await self._exchange_code_for_token(
            code=code,
            code_verifier=code_verifier,
        )
        github_user = await self._fetch_user(access_token=token.access_token)
        email = await self._fetch_primary_email(access_token=token.access_token)
        user = await self._get_or_create_user(
            github_id=github_user.id,
            username=github_user.login,
            email=email,
        )

        return self.auth_manager.generate_jwt(
            input_data={
                "sub": user.username,
                "role": user.role.value,
            },
        )

    async def _exchange_code_for_token(
            self,
            code: str,
            code_verifier: str,
    ) -> GithubTokenDTO:
        """
        Exchange authorization code for access token.

        :param code: authorization code
        :param code_verifier: PKCE code verifier

        :return: GitHub token payload
        """
        data = self._build_token_payload(
            code=code,
            code_verifier=code_verifier,
        )
        headers = self._build_token_headers()

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.github.token_url,
                data=data,
                headers=headers,
            )

        if response.status_code != 200:
            raise OAuthTokenExchangeError(
                detail="Failed to exchange code for access token.",
            )

        token = GithubTokenDTO.model_validate(response.json())
        if not token.access_token:
            raise OAuthTokenMissingError(detail="GitHub access token is missing.")

        return token

    async def _fetch_user(self, access_token: str) -> GithubUserDTO:
        """
        Fetch GitHub user profile.

        :param access_token: GitHub access token

        :return: GitHub user payload
        """
        headers = self._build_api_headers(access_token=access_token)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                settings.github.user_url,
                headers=headers,
            )

        if response.status_code != 200:
            raise OAuthUserFetchError(detail="Failed to fetch GitHub user profile.")

        return GithubUserDTO.model_validate(response.json())

    async def _fetch_primary_email(self, access_token: str) -> str:
        """
        Fetch primary verified GitHub email.

        :param access_token: GitHub access token

        :return: primary verified email
        """
        headers = self._build_api_headers(access_token=access_token)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                settings.github.emails_url,
                headers=headers,
            )

        if response.status_code != 200:
            raise OAuthEmailFetchError(detail="Failed to fetch GitHub email list.")

        payload = response.json()
        if not isinstance(payload, list):
            raise OAuthEmailFetchError(detail="GitHub email response is invalid.")
        for item in payload:
            email = GithubEmailDTO.model_validate(item)
            if email.primary and email.verified:
                return email.email

        raise OAuthEmailNotVerifiedError(detail="GitHub account has no verified email.")

    async def _get_or_create_user(
            self,
            github_id: int,
            username: str,
            email: str,
    ) -> User:
        """
        Get existing user or create a new one for GitHub OAuth.

        :param github_id: GitHub user id
        :param username: GitHub username
        :param email: GitHub verified email

        :return: user model
        """
        existing_by_github = await self.user_repository.get_by_github_id(github_id=github_id)

        if existing_by_github:
            return existing_by_github

        existing_by_username = await self.user_repository.get_by_username(username=username)

        if existing_by_username:
            raise OAuthAccountConflict(detail=f'Account already exists with username "{username}".')

        existing_by_email = await self.user_repository.get_by_email(email=email)

        if existing_by_email:
            raise OAuthAccountConflict(detail=f'Account already exists with email "{email}".')

        user = User(
            username=username,
            email=email,
            github_id=github_id,
            hashed_password=None,
            role=UserRole.USER,
        )

        await self.user_repository.add(model=user)
        await self.user_repository.session.commit()
        await self.user_repository.session.refresh(instance=user)

        return user

    @staticmethod
    def _build_authorize_params(state: str, code_challenge: str) -> dict[str, str]:
        """
        Build OAuth authorize params.

        :param state: OAuth state
        :param code_challenge: PKCE code challenge

        :return: params dictionary
        """
        return {
            "client_id": settings.github.client_id,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "allow_signup": "true" if settings.github.allow_signup else "false",
            "scope": settings.github.scope,
            "redirect_uri": settings.github.redirect_uri,
        }

    @staticmethod
    def _build_token_payload(code: str, code_verifier: str) -> dict[str, str]:
        """
        Build token exchange payload.

        :param code: authorization code
        :param code_verifier: PKCE code verifier

        :return: payload dictionary
        """
        return {
            "client_id": settings.github.client_id,
            "client_secret": settings.github.client_secret,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.github.redirect_uri,
        }

    @staticmethod
    def _build_token_headers() -> dict[str, str]:
        """
        Build token exchange headers.

        :return: headers dictionary
        """
        return {"Accept": "application/json"}

    @staticmethod
    def _build_api_headers(access_token: str) -> dict[str, str]:
        """
        Build GitHub API headers.

        :param access_token: GitHub access token

        :return: headers dictionary
        """
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }

    @staticmethod
    def _ensure_configured() -> None:
        """
        Ensure GitHub OAuth settings are configured.

        :return: None
        """
        if not settings.github.client_id:
            raise OAuthConfigError(detail="GitHub client id is not configured.")
        if not settings.github.client_secret:
            raise OAuthConfigError(detail="GitHub client secret is not configured.")
        if not settings.github.redirect_uri:
            raise OAuthConfigError(detail="GitHub redirect uri is not configured.")
