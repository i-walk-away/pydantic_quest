from fastapi import Depends

from src.app.core.dependencies.repositories.lesson_progress import (
    get_lesson_progress_repository,
)
from src.app.domain.repositories.lesson_progress_repository import (
    LessonProgressRepository,
)
from src.app.domain.services.lesson_progress_service import LessonProgressService


def get_lesson_progress_service(
        repository: LessonProgressRepository = Depends(get_lesson_progress_repository),
) -> LessonProgressService:
    """
    Build lesson progress service.

    :param repository: lesson progress repository

    :return: lesson progress service
    """
    return LessonProgressService(progress_repository=repository)
