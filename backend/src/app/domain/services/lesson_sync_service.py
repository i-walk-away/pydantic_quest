from src.app.content import LessonsLoader
from src.app.domain.models.dto.lesson import LessonSyncResultDTO
from src.app.domain.repositories.lesson_repository import LessonRepository
from src.app.domain.services.lesson_sync_diff_builder import LessonSyncDiffBuilder
from src.app.domain.services.lesson_sync_importer import LessonSyncImporter


class LessonSyncService:
    def __init__(
            self,
            loader: LessonsLoader,
            lesson_repository: LessonRepository,
            diff_builder: LessonSyncDiffBuilder,
            importer: LessonSyncImporter,
    ) -> None:
        """
        Initialize lesson sync service.

        :param loader: lessons loader
        :param lesson_repository: lesson repository
        :param diff_builder: lesson sync diff builder
        :param importer: lesson sync importer

        :return: None
        """
        self.loader = loader
        self.repository = lesson_repository
        self.diff_builder = diff_builder
        self.importer = importer

    async def sync(
            self,
            *,
            delete_missing: bool = True,
            dry_run: bool = False,
    ) -> LessonSyncResultDTO:
        """
        Sync lessons from files to database.

        When delete_missing is enabled, the database is treated as a projection
        of the repository content and obsolete rows are removed automatically.

        :param delete_missing: delete lessons not present in files
        :param dry_run: preview sync result without writes

        :return: sync counters
        """
        loaded_lessons = self.loader.load()
        existing_lessons = await self.repository.get_all()
        diff = self.diff_builder.build(
            loaded_lessons=loaded_lessons,
            existing_lessons=existing_lessons,
            delete_missing=delete_missing,
        )

        if dry_run:
            return self.importer.preview(diff=diff)

        return await self.importer.apply(diff=diff)
