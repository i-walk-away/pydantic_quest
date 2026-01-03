from uuid import UUID

from fastapi import APIRouter, Depends

from src.app.backend.core.dependencies.services.lesson import get_lesson_service
from src.app.backend.models.dto.lesson import LessonDTO, CreateLessonDTO
from src.app.backend.services.lesson import LessonService


def build_lesson_router(
        prefix: str,
        tags: list[str],
        dependencies: list
) -> APIRouter:
    """
    Build a lessons router with shared handlers.

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
            lesson_service: LessonService = Depends(
                dependency=get_lesson_service
            )
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
            lesson_service: LessonService = Depends(
                dependency=get_lesson_service
            )
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
            lesson_service: LessonService = Depends(
                dependency=get_lesson_service
            )
    ) -> LessonDTO:
        """
        Get lesson by id.

        :param lesson_id: lesson id
        :param lesson_service: lesson service
        :return: lesson
        """
        lesson = await lesson_service.get_by_id(id=lesson_id)

        return lesson

    return router
