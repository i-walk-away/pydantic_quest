from sqlalchemy.ext.asyncio import AsyncSession

from src.app.backend.models.db.lesson import Lesson
from src.app.backend.repositories.base import BaseRepository


class LessonRepository(BaseRepository[Lesson]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model=Lesson
        )
