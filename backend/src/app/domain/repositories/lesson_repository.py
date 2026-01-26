from sqlalchemy import select
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

    async def get_by_slug(self, slug: str) -> Lesson | None:
        """
        Get lesson by slug.

        :param slug: lesson slug

        :return: lesson or None
        """
        stmt = select(Lesson).where(Lesson.slug == slug)
        return await self.session.scalar(stmt)
