from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.dto.lesson import LessonSyncDiffDTO, LessonSyncResultDTO
from src.app.domain.repositories.lesson_repository import LessonRepository


class LessonSyncImporter:
    def __init__(self, lesson_repository: LessonRepository) -> None:
        """
        Initialize lesson sync importer.

        :param lesson_repository: lesson repository

        :return: None
        """
        self.repository = lesson_repository

    async def apply(self, diff: LessonSyncDiffDTO) -> LessonSyncResultDTO:
        """
        Apply sync diff to database.

        This service executes persistence side effects while keeping orchestration
        and diff computation outside of repository writes.

        :param diff: sync diff

        :return: sync result
        """
        for payload in diff.create_payloads:
            lesson = Lesson(**payload.model_dump())
            await self.repository.add(model=lesson)

        for update_item in diff.update_payloads:
            await self.repository.update(
                id=update_item.lesson_id,
                data=update_item.payload.model_dump(),
            )

        deleted = 0
        for lesson_id in diff.delete_ids:
            if await self.repository.delete(id=lesson_id):
                deleted += 1

        await self.repository.session.commit()

        return LessonSyncResultDTO(
            created=len(diff.create_payloads),
            updated=len(diff.update_payloads),
            deleted=deleted,
            unchanged=diff.unchanged,
            total=diff.total,
            dry_run=False,
        )

    @staticmethod
    def preview(diff: LessonSyncDiffDTO) -> LessonSyncResultDTO:
        """
        Build dry-run result without database side effects.

        :param diff: sync diff

        :return: dry-run sync result
        """

        return LessonSyncResultDTO(
            created=len(diff.create_payloads),
            updated=len(diff.update_payloads),
            deleted=len(diff.delete_ids),
            unchanged=diff.unchanged,
            total=diff.total,
            dry_run=True,
        )
