from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.dependencies.db import get_session
from src.app.domain.repositories.lesson import LessonRepository


def get_lesson_repository(
        session: AsyncSession = Depends(get_session)
) -> LessonRepository:
    """
    Constructs an instance of ``LessonRepository`` with SQLA Async Session injected.
    """

    return LessonRepository(session=session)
