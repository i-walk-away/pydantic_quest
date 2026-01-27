from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.models.db.lesson_progress import LessonProgress
from src.app.domain.repositories.base_repository import BaseRepository


class LessonProgressRepository(BaseRepository[LessonProgress]):
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize lesson progress repository.

        :param session: database session

        :return: None
        """
        super().__init__(
            session=session,
            model=LessonProgress,
        )

    async def get_completed_lesson_ids(self, user_id: UUID) -> list[UUID]:
        """
        Get completed lesson ids for user.

        :param user_id: user id

        :return: list of lesson ids
        """
        stmt = select(LessonProgress.lesson_id).where(LessonProgress.user_id == user_id)
        result = await self.session.scalars(stmt)

        return list(result.all())

    async def exists(self, user_id: UUID, lesson_id: UUID) -> bool:
        """
        Check if progress exists.

        :param user_id: user id
        :param lesson_id: lesson id

        :return: True if progress exists
        """
        stmt = (
            select(LessonProgress.id)
            .where(LessonProgress.user_id == user_id)
            .where(LessonProgress.lesson_id == lesson_id)
        )
        result = await self.session.scalar(stmt)

        return result is not None

    async def reset_for_user(self, user_id: UUID) -> int:
        """
        Delete all progress for user.

        :param user_id: user id

        :return: deleted rows count
        """
        stmt = delete(LessonProgress).where(LessonProgress.user_id == user_id)
        result = await self.session.execute(stmt)

        return result.rowcount or 0
