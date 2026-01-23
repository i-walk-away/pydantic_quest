from fastapi import Depends

from src.app.core.dependencies.repositories.user import get_user_repository
from src.app.core.dependencies.security.auth_manager import get_auth_manager
from src.app.core.security.auth_manager import AuthManager
from src.app.domain.repositories import UserRepository
from src.app.domain.services import AuthService


def get_auth_service(
        repository: UserRepository = Depends(get_user_repository),
        auth_manager: AuthManager = Depends(get_auth_manager),
) -> AuthService:
    """
    Constructs an instance of AuthService with UserRepository and AuthManager
    injected.
    """
    return AuthService(user_repository=repository, auth_manager=auth_manager)
