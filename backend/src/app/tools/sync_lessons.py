import asyncio
import json
import sys
from pathlib import Path

from src.app.content.loader import LessonsLoader
from src.app.content.validator import LessonsContentValidator
from src.app.core.dependencies.db import session_factory
from src.app.domain.repositories.lesson_repository import LessonRepository
from src.app.domain.services.lesson_sync_diff_builder import LessonSyncDiffBuilder
from src.app.domain.services.lesson_sync_importer import LessonSyncImporter
from src.app.domain.services.lesson_sync_service import LessonSyncService
from src.cfg.cfg import settings


async def run_sync() -> dict[str, int | bool]:
    """
    Run lessons sync from files to database.

    :return: sync counters
    """
    async with session_factory() as session:
        repository = LessonRepository(session=session)
        loader = LessonsLoader(
            root_dir=Path(settings.lessons_dir).resolve(),
            validator=LessonsContentValidator(),
        )
        service = LessonSyncService(
            loader=loader,
            lesson_repository=repository,
            diff_builder=LessonSyncDiffBuilder(),
            importer=LessonSyncImporter(lesson_repository=repository),
        )
        result = await service.sync(delete_missing=True)

        return result.model_dump()


def main() -> None:
    """
    Run sync command-line entrypoint.

    :return: None
    """
    result = asyncio.run(run_sync())
    sys.stdout.write(f"{json.dumps(result)}\n")


if __name__ == "__main__":
    main()
