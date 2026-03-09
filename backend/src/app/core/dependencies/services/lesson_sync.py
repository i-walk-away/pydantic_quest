from pathlib import Path

from fastapi import Depends

from src.app.content import LessonsLoader
from src.app.content.validator import LessonsContentValidator
from src.app.core.dependencies.repositories.lesson import get_lesson_repository
from src.app.domain.repositories.lesson_repository import LessonRepository
from src.app.domain.services.lesson_sync_diff_builder import LessonSyncDiffBuilder
from src.app.domain.services.lesson_sync_importer import LessonSyncImporter
from src.app.domain.services.lesson_sync_service import LessonSyncService
from src.cfg.cfg import settings


def get_lessons_content_validator() -> LessonsContentValidator:
    """
    Build lessons content validator.

    :return: lessons content validator
    """

    return LessonsContentValidator()


def get_lessons_loader(
        validator: LessonsContentValidator = Depends(get_lessons_content_validator),
) -> LessonsLoader:
    """
    Build a lessons loader.

    :param validator: lessons content validator

    :return: lessons loader
    """

    return LessonsLoader(root_dir=Path(settings.lessons_dir).resolve(), validator=validator)


def get_lesson_sync_diff_builder() -> LessonSyncDiffBuilder:
    """
    Build lesson sync diff builder.

    :return: lesson sync diff builder
    """

    return LessonSyncDiffBuilder()


def get_lesson_sync_importer(
        repository: LessonRepository = Depends(get_lesson_repository),
) -> LessonSyncImporter:
    """
    Build lesson sync importer.

    :param repository: lesson repository

    :return: lesson sync importer
    """

    return LessonSyncImporter(lesson_repository=repository)


def get_lesson_sync_service(
        loader: LessonsLoader = Depends(get_lessons_loader),
        repository: LessonRepository = Depends(get_lesson_repository),
        diff_builder: LessonSyncDiffBuilder = Depends(get_lesson_sync_diff_builder),
        importer: LessonSyncImporter = Depends(get_lesson_sync_importer),
) -> LessonSyncService:
    """
    Build a lesson sync service.

    The provider wires pure content loading, diff calculation, and persistence
    applying into one orchestration service used by API and CLI entry points.

    :param loader: lessons loader
    :param repository: lesson repository
    :param diff_builder: lesson sync diff builder
    :param importer: lesson sync importer

    :return: lesson sync service
    """

    return LessonSyncService(
        loader=loader,
        lesson_repository=repository,
        diff_builder=diff_builder,
        importer=importer,
    )
