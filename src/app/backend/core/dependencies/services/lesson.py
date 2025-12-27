from fastapi import Depends

from src.app.backend.core.dependencies.repositories.lesson import get_lesson_repository
from src.app.backend.repositories.lesson import LessonRepository
from src.app.backend.services.lesson import LessonService


def get_lesson_service(
        repository: LessonRepository = Depends(get_lesson_repository)
) -> LessonService:
    """

    :param repository:
    :return:
    """
    return LessonService(lesson_repository=repository)
