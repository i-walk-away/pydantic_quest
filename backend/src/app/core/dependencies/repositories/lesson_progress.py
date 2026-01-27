from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.dependencies.db import get_session
from src.app.domain.repositories.lesson_progress_repository import LessonProgressRepository


def get_lesson_progress_repository(
        session: AsyncSession = Depends(get_session),
) -> LessonProgressRepository:
    """
    Build lesson progress repository.

    :param session: database session

    :return: lesson progress repository
    """
    return LessonProgressRepository(session=session)
