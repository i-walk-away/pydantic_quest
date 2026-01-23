from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.models.db.lesson import Lesson
from src.app.domain.repositories.base_repository import BaseRepository


class LessonRepository(BaseRepository[Lesson]):
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize lesson repository.

        :param session: database session

        :return: None
        """
        super().__init__(
            session=session,
            model=Lesson,
        )
