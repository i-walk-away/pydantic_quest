from pathlib import Path

import yaml

from src.app.content.models import (
    LessonCasesFile,
    LessonMetaFile,
    LessonsIndexFile,
    LoadedLesson,
)
from src.app.content.validator import LessonsContentValidator
from src.app.domain.lesson_order import lesson_order_key

LESSON_META_FILENAME = "lesson.yaml"
LESSON_THEORY_FILENAME = "theory.md"
LESSON_STARTER_FILENAME = "starter.py"
LESSON_CASES_FILENAME = "cases.yaml"


class LessonsLoader:
    def __init__(self, root_dir: Path, validator: LessonsContentValidator) -> None:
        """
        Initialize lessons loader.

        :param root_dir: lessons root directory
        :param validator: lessons content validator

        :return: None
        """
        self.root_dir = root_dir
        self.validator = validator

    def load(self) -> list[LoadedLesson]:
        """
        Load and validate all lessons from files.

        The loader keeps lesson authoring file-based for contributors while
        still producing validated models for synchronization services.

        :return: loaded lessons
        """
        index_path = self.root_dir / "index.yaml"
        index_payload = self._read_yaml(path=index_path)
        index_file = LessonsIndexFile.model_validate(obj=index_payload)
        self.validator.validate_index(index_file=index_file)

        lessons = []
        for index_item in index_file.lessons:
            lesson_dir = self.root_dir / index_item.slug
            lesson_meta = self._load_meta(lesson_dir=lesson_dir)
            lesson_cases = self._load_cases(lesson_dir=lesson_dir, no_code=index_item.no_code)
            theory = self._read_text(path=lesson_dir / LESSON_THEORY_FILENAME)
            starter_code = self._read_text(path=lesson_dir / LESSON_STARTER_FILENAME)
            lessons.append(
                LoadedLesson(
                    slug=index_item.slug,
                    order=index_item.order,
                    no_code=index_item.no_code,
                    name=lesson_meta.title,
                    body_markdown=theory,
                    code_editor_default=starter_code,
                    cases=lesson_cases.cases,
                    source_dir=lesson_dir,
                ),
            )

        lessons.sort(key=lambda item: lesson_order_key(item.order))

        return lessons

    def _load_meta(self, lesson_dir: Path) -> LessonMetaFile:
        """
        Load lesson metadata file.

        :param lesson_dir: lesson directory path

        :return: lesson metadata
        """
        payload = self._read_yaml(path=lesson_dir / LESSON_META_FILENAME)

        return LessonMetaFile.model_validate(obj=payload)

    def _load_cases(self, lesson_dir: Path, *, no_code: bool) -> LessonCasesFile:
        """
        Load lesson cases file.

        :param lesson_dir: lesson directory path
        :param no_code: lesson has no coding task

        :return: lesson cases
        """
        cases_path = lesson_dir / LESSON_CASES_FILENAME

        if no_code and not cases_path.exists():
            return LessonCasesFile(cases=[])

        payload = self._read_yaml(path=cases_path)

        return LessonCasesFile.model_validate(obj=payload)

    @staticmethod
    def _read_yaml(path: Path) -> dict:
        """
        Read YAML file as dictionary.

        Strict mapping-only payloads are enforced to keep content schema
        errors explicit for lesson contributors.

        :param path: yaml file path

        :return: parsed yaml payload
        """

        if not path.exists():
            raise FileNotFoundError(path)

        content = path.read_text(encoding="utf-8")
        payload = yaml.safe_load(stream=content) or {}
        if not isinstance(payload, dict):
            message = f"yaml root must be mapping: {path}"
            raise TypeError(message)

        return payload

    @staticmethod
    def _read_text(path: Path) -> str:
        """
        Read plain text file.

        :param path: text file path

        :return: text content
        """

        if not path.exists():
            raise FileNotFoundError(path)

        return path.read_text(encoding="utf-8")
