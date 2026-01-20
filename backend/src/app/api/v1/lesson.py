from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.core.dependencies.services.lesson import get_lesson_service
from src.app.domain.models.dto.lesson import (
    CreateLessonDTO,
    LessonDTO,
    UpdateLessonDTO,
)
from src.app.domain.services.lesson_service import LessonService

router = APIRouter(
    prefix="/lessons",
    tags=["Lessons"],
    dependencies=[],
)


@router.post(path="/create", summary="Create new lesson")
async def create_lesson(
        data: CreateLessonDTO,
        lesson_service: LessonService = Depends(dependency=get_lesson_service)
) -> LessonDTO:
    """
    Create lesson.

    :param data: lesson creation data
    :param lesson_service: lesson service

    :return: created lesson
    """
    lesson = await lesson_service.create(schema=data)

    return lesson


@router.get(path="/get_all", summary="Get all lessons")
async def get_all_lessons(
        lesson_service: LessonService = Depends(dependency=get_lesson_service)
) -> list[LessonDTO]:
    """
    Get all lessons.

    :param lesson_service: lesson service

    :return: lesson list
    """
    lessons = await lesson_service.get_all()

    return lessons


@router.get(path="/{lesson_id}", summary="Get lesson by id")
async def get_lesson_by_id(
        lesson_id: UUID,
        lesson_service: LessonService = Depends(dependency=get_lesson_service)
) -> LessonDTO:
    """
    Get lesson by id.

    :param lesson_id: lesson id
    :param lesson_service: lesson service

    :return: lesson
    """
    lesson = await lesson_service.get_by_id(id=lesson_id)

    return lesson


@router.put(path="/{lesson_id}", summary="Update lesson")
async def update_lesson(
        lesson_id: UUID,
        data: UpdateLessonDTO,
        lesson_service: LessonService = Depends(dependency=get_lesson_service)
) -> LessonDTO:
    """
    Update lesson.

    :param lesson_id: lesson id
    :param data: lesson update data
    :param lesson_service: lesson service

    :return: updated lesson
    """
    lesson = await lesson_service.update(id=lesson_id, schema=data)

    return lesson


@router.delete(path="/{lesson_id}", summary="Delete lesson")
async def delete_lesson(
        lesson_id: UUID,
        lesson_service: LessonService = Depends(dependency=get_lesson_service)
) -> bool:
    """
    Delete lesson.

    :param lesson_id: lesson id
    :param lesson_service: lesson service

    :return: ``True`` if lesson was deleted
    """
    return await lesson_service.delete(id=lesson_id)
