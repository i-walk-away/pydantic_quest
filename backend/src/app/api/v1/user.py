from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.core.dependencies.security.user import get_user_from_jwt, require_admin_user
from src.app.core.dependencies.services.lesson_progress import get_lesson_progress_service
from src.app.core.dependencies.services.user import get_user_service
from src.app.domain.models.dto.user import CreateUserDTO, UpdateUserDTO, UserDTO
from src.app.domain.services.lesson_progress_service import LessonProgressService
from src.app.domain.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[])


@router.post(path="/create", summary="Create new user")
async def create_user(
        data: CreateUserDTO,
        user_service: UserService = Depends(dependency=get_user_service),
) -> UserDTO:
    user = await user_service.create(schema=data)
    return user


@router.get(path="/get_all", summary="Get all users")
async def get_all_users(
        user_service: UserService = Depends(dependency=get_user_service),
) -> list[UserDTO]:
    return await user_service.get_all()


@router.get(path="/me", summary="Get current user")
async def get_me(user: UserDTO = Depends(dependency=get_user_from_jwt)) -> UserDTO:
    return user


@router.put(path="/me", summary="Update current user")
async def update_me(
        data: UpdateUserDTO,
        user: UserDTO = Depends(dependency=get_user_from_jwt),
        user_service: UserService = Depends(dependency=get_user_service),
) -> UserDTO:
    updated_user = await user_service.update_me(id=user.id, schema=data)
    return updated_user


@router.get(path="/me/progress", summary="Get current user progress")
async def get_my_progress(
        user: UserDTO = Depends(dependency=get_user_from_jwt),
        progress_service: LessonProgressService = Depends(get_lesson_progress_service),
) -> list[UUID]:
    return await progress_service.get_completed_lesson_ids(user_id=user.id)


@router.post(path="/me/progress/{lesson_id}", summary="Mark lesson completed")
async def mark_lesson_completed(
        lesson_id: UUID,
        user: UserDTO = Depends(dependency=get_user_from_jwt),
        progress_service: LessonProgressService = Depends(get_lesson_progress_service),
) -> dict[str, bool]:
    await progress_service.mark_completed(user_id=user.id, lesson_id=lesson_id)
    return {"ok": True}


@router.post(path="/me/progress/reset", summary="Reset current user progress")
async def reset_my_progress(
        user: UserDTO = Depends(dependency=get_user_from_jwt),
        progress_service: LessonProgressService = Depends(get_lesson_progress_service),
) -> dict[str, int]:
    deleted = await progress_service.reset_progress(user_id=user.id)
    return {"deleted": deleted}


@router.get(path="/{user_id}", summary="Get user by id")
async def get_user_by_id(
        user_id: UUID,
        user_service: UserService = Depends(dependency=get_user_service),
) -> UserDTO:
    return await user_service.get_by_id(id=user_id)


@router.delete(path="/{user_id}", summary="Delete user")
async def delete_user(
        user_id: UUID,
        user_service: UserService = Depends(dependency=get_user_service),
        _admin: UserDTO = Depends(require_admin_user),
) -> bool:
    return await user_service.delete(id=user_id)
