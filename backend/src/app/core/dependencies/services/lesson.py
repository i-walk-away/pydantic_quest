from fastapi import Depends

from src.app.core.dependencies.repositories.lesson import get_lesson_repository
from src.app.domain.repositories.lesson_repository import LessonRepository
from src.app.domain.services.lesson_service import LessonService


def get_lesson_service(
        repository: LessonRepository = Depends(get_lesson_repository)
) -> LessonService:
    """
    Build a lesson service.

    :param repository: lesson repository

    :return: lesson service
    """
    return LessonService(lesson_repository=repository)
