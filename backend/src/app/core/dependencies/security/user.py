from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode
from jwt.exceptions import InvalidTokenError

from src.app.core.dependencies.services.user import get_user_service
from src.app.core.exceptions.auth_exc import InvalidCredentials, Unauthorized
from src.app.core.exceptions.base_exc import NotFoundError
from src.app.domain.models.dto.user import UserDTO
from src.app.domain.models.enums.role import UserRole
from src.app.domain.services import UserService
from src.cfg.cfg import settings

scheme_factory = HTTPBearer(auto_error=False)


async def get_user_from_jwt(
        user_service: UserService = Depends(get_user_service),
        jwt: HTTPAuthorizationCredentials = Depends(scheme_factory),
) -> UserDTO:
    """
    Gets user from the given JSON Web Token.

    :param user_service:
    :param jwt:
    :return:
    """
    if not jwt:
        raise InvalidCredentials

    try:
        decoded_token: dict = decode(
            jwt=jwt.credentials,
            key=settings.auth.jwt_secret_key,
            algorithms=[settings.auth.jwt_algorithm],
        )
        username = decoded_token.get('sub')
        if not username:
            raise InvalidCredentials
    except InvalidTokenError as e:
        raise InvalidCredentials from e

    try:
        user = await user_service.get_by_username(username=username)
    except NotFoundError as e:
        raise InvalidCredentials from e

    return user


async def get_optional_user_from_jwt(
        user_service: UserService = Depends(get_user_service),
        jwt: HTTPAuthorizationCredentials | None = Depends(scheme_factory),
) -> UserDTO | None:
    """
    Gets optional user from the given JSON Web Token.

    :param user_service: user service
    :param jwt: authorization credentials

    :return: user dto or None
    """
    if not jwt:
        return None

    return await get_user_from_jwt(
        user_service=user_service,
        jwt=jwt,
    )


async def require_admin_user(
        user: UserDTO = Depends(get_user_from_jwt),
) -> UserDTO:
    """
    Ensure that the current user has admin role.

    :param user: authenticated user

    :return: authenticated admin user
    """
    if user.role != UserRole.ADMIN:
        raise Unauthorized

    return user
