from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.core.dependencies.security.user import require_admin_user
from src.app.core.dependencies.services.user import get_user_service
from src.app.domain.models.dto.user import (
    CreateUserDTO,
    UserDTO,
    # UpdateUserDTO,
)
from src.app.domain.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[],
)


@router.post(path="/create", summary="Create new user")
async def create_user(
        data: CreateUserDTO,
        user_service: UserService = Depends(dependency=get_user_service),
        # _admin: UserDTO = Depends(require_admin_user)
) -> UserDTO:
    """
    Create user.

    :param data: user creation data
    :param user_service: user service

    :return: created user
    """
    user = await user_service.create(schema=data)

    return user


@router.get(path="/get_all", summary="Get all users")
async def get_all_users(
        user_service: UserService = Depends(dependency=get_user_service)
) -> list[UserDTO]:
    """
    Get all users.

    :param user_service: user service

    :return: user list
    """
    users = await user_service.get_all()

    return users


@router.get(path="/{user_id}", summary="Get user by id")
async def get_user_by_id(
        user_id: UUID,
        user_service: UserService = Depends(dependency=get_user_service)
) -> UserDTO:
    """
    Get user by id.

    :param user_id: user id
    :param user_service: user service

    :return: user
    """
    user = await user_service.get_by_id(id=user_id)

    return user


# @router.put(path="/{user_id}", summary="Update user")
# async def update_user(
#         user_id: UUID,
#         data: UpdateUserDTO,
#         user_service: UserService = Depends(dependency=get_user_service),
#         _admin: UserDTO = Depends(require_admin_user)
# ) -> UserDTO:
#     """
#     Update user.
#
#     :param user_id: user id
#     :param data: user update data
#     :param user_service: user service
#     :param _admin: authenticated admin user
#
#     :return: updated user
#     """
#     user = await user_service.update(id=user_id, schema=data)
#
#     return user


@router.delete(path="/{user_id}", summary="Delete user")
async def delete_user(
        user_id: UUID,
        user_service: UserService = Depends(dependency=get_user_service),
        _admin: UserDTO = Depends(require_admin_user)
) -> bool:
    """
    Delete user.

    :param user_id: user id
    :param user_service: user service
    :param _admin: authenticated admin user

    :return: True if user was deleted
    """
    return await user_service.delete(id=user_id)
