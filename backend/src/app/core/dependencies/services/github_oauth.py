from fastapi import Depends

from src.app.core.dependencies.repositories.user import get_user_repository
from src.app.core.dependencies.security.auth_manager import get_auth_manager
from src.app.core.security.auth_manager import AuthManager
from src.app.domain.repositories import UserRepository
from src.app.domain.services.github_oauth_service import GithubOAuthService


def get_github_oauth_service(
        repository: UserRepository = Depends(get_user_repository),
        auth_manager: AuthManager = Depends(get_auth_manager),
) -> GithubOAuthService:
    """
    Build a GitHub OAuth service with repository and auth manager injected.

    :param repository: user repository
    :param auth_manager: auth manager

    :return: GitHub OAuth service
    """
    return GithubOAuthService(user_repository=repository, auth_manager=auth_manager)
