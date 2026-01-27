from uuid import UUID

from src.app.domain.models.db.lesson_progress import LessonProgress
from src.app.domain.repositories.lesson_progress_repository import LessonProgressRepository


class LessonProgressService:
    def __init__(self, progress_repository: LessonProgressRepository) -> None:
        """
        Initialize lesson progress service.

        :param progress_repository: progress repository

        :return: None
        """
        self.repository = progress_repository

    async def mark_completed(self, user_id: UUID, lesson_id: UUID) -> None:
        """
        Mark lesson completed for user.

        :param user_id: user id
        :param lesson_id: lesson id

        :return: None
        """
        exists = await self.repository.exists(
            user_id=user_id,
            lesson_id=lesson_id,
        )
        if exists:
            return

        progress = LessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
        )
        await self.repository.add(progress)
        await self.repository.session.commit()

    async def get_completed_lesson_ids(self, user_id: UUID) -> list[UUID]:
        """
        Get completed lesson ids for user.

        :param user_id: user id

        :return: list of lesson ids
        """
        return await self.repository.get_completed_lesson_ids(user_id=user_id)

    async def reset_progress(self, user_id: UUID) -> int:
        """
        Reset lesson progress for user.

        :param user_id: user id

        :return: number of deleted rows
        """
        deleted = await self.repository.reset_for_user(user_id=user_id)
        await self.repository.session.commit()

        return deleted
