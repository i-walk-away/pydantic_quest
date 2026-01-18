from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.core.dependencies.services.lesson import get_lesson_service
from src.app.domain.models.dto.lesson import (
    LessonDTO,
    CreateLessonDTO,
    UpdateLessonDTO,
)
from src.app.domain.services.lesson_service import LessonService


def build_lesson_router(
        prefix: str,
        tags: list[str],
        dependencies: list
) -> APIRouter:
    """
    Build a lessons router with shared handlers. This approach allows
    to connect the same router to different entry points with variable
    dependencies, tags and prefixes.

    :param prefix: router prefix
    :param tags: router tags
    :param dependencies: router dependencies

    :return: configured lessons router
    """
    router = APIRouter(
        prefix=prefix,
        tags=tags,
        dependencies=dependencies
    )

    @router.post(path='/create', summary='Create new lesson')
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

    @router.get(path='/get_all', summary='Get all lessons')
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

    @router.get(path='/get_by_id', summary='Get lesson by id')
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

    @router.put(path='/update', summary='Update lesson')
    async def update_lesson(
            data: UpdateLessonDTO,
            lesson_service: LessonService = Depends(dependency=get_lesson_service)
    ) -> LessonDTO:
        """
        Update lesson.

        :param data: lesson update data
        :param lesson_service: lesson service

        :return: updated lesson
        """
        lesson = await lesson_service.update(schema=data)

        return lesson

    @router.delete(path='/delete', summary='Delete lesson')
    async def delete_lesson(
            lesson_id: UUID,
            lesson_service: LessonService = Depends(dependency=get_lesson_service)
    ) -> None:
        """
        Delete lesson.

        :param lesson_id: lesson id
        :param lesson_service: lesson service

        :return: None
        """
        await lesson_service.delete(id=lesson_id)

    return router
