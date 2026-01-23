from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from src.app.core.dependencies.services.auth import get_auth_service
from src.app.core.dependencies.services.github_oauth import get_github_oauth_service
from src.app.core.exceptions.oauth_exc import OAuthStateError
from src.app.core.security.oauth_state import (
    build_code_challenge,
    create_oauth_state,
    parse_oauth_state,
)
from src.app.domain.models.dto.auth import (
    GithubOAuthCallbackDTO,
    LoginCredentials,
    LoginResponse,
)
from src.app.domain.services import AuthService, GithubOAuthService
from src.cfg.cfg import settings

router = APIRouter(prefix='/auth', tags=['Auth'])
OAUTH_COOKIE_NAME: str = "github_oauth_state"


@router.post(path='/login', summary='login')
async def login(
        credentials: LoginCredentials,
        auth_service: AuthService = Depends(dependency=get_auth_service),
) -> LoginResponse:
    """
    Login user with username and password.

    :param credentials: login credentials
    :param auth_service: auth service

    :return: login response
    """
    jwt_token = await auth_service.login(credentials=credentials)

    return LoginResponse(access_token=jwt_token)


@router.get(path="/github", summary="GitHub OAuth login")
async def github_login(
        github_oauth_service: GithubOAuthService = Depends(dependency=get_github_oauth_service),
) -> RedirectResponse:
    """
    Redirect user to GitHub OAuth login page.

    :param github_oauth_service: GitHub OAuth service

    :return: redirect response
    """
    state, code_verifier, cookie_value = create_oauth_state(
        secret=settings.auth.jwt_secret_key,
    )
    authorize_url = github_oauth_service.build_authorize_url(
        state=state,
        code_challenge=build_code_challenge(code_verifier=code_verifier),
    )

    response = RedirectResponse(url=authorize_url, status_code=302)
    response.set_cookie(
        key=OAUTH_COOKIE_NAME,
        value=cookie_value,
        httponly=True,
        samesite="lax",
        max_age=600,
        path="/api/v1/auth",
    )

    return response


@router.get(path="/github/callback", summary="GitHub OAuth callback")
async def github_callback(
        request: Request,
        payload: GithubOAuthCallbackDTO = Depends(),
        github_oauth_service: GithubOAuthService = Depends(get_github_oauth_service),
) -> RedirectResponse:
    """
    Handle GitHub OAuth callback and issue JWT.

    :param request: request object
    :param payload: OAuth callback payload
    :param github_oauth_service: GitHub OAuth service

    :return: redirect response
    """
    cookie_value = request.cookies.get(OAUTH_COOKIE_NAME)
    if not cookie_value:
        raise OAuthStateError

    code_verifier = parse_oauth_state(
        secret=settings.auth.jwt_secret_key,
        cookie_value=cookie_value,
        state=payload.state,
    )
    if not code_verifier:
        raise OAuthStateError

    jwt_token = await github_oauth_service.authenticate(
        code=payload.code,
        code_verifier=code_verifier,
    )

    query = urlencode({"token": jwt_token})
    redirect_url = f"{settings.frontend_url}?{query}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.delete_cookie(key=OAUTH_COOKIE_NAME, path="/api/v1/auth")

    return response
