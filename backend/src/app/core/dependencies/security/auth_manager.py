from fastapi import Depends
from passlib.context import CryptContext

from src.app.core.dependencies.security.crypt_context import get_crypt_context
from src.app.core.security.auth_manager import AuthManager


def get_auth_manager(
        context: CryptContext = Depends(get_crypt_context),
) -> AuthManager:
    """
    Constructs an instance of AuthManager with passlib.CryptContext injected.

    :return: AuthManager object.
    """
    return AuthManager(context=context)
