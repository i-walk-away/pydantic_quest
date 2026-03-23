from pathlib import Path

import yaml

from src.app.content.models import (
    LessonCasesFile,
    LessonMetaFile,
    LessonQuizFile,
    LessonsIndexFile,
    LoadedLesson,
)
from src.app.content.validator import LessonsContentValidator
from src.app.domain.lesson_order import lesson_order_key

LESSON_META_FILENAME = "lesson.yaml"
LESSON_THEORY_FILENAME = "theory.md"
LESSON_STARTER_FILENAME = "starter.py"
LESSON_CASES_FILENAME = "cases.yaml"
LESSON_QUIZ_FILENAME = "quiz.yaml"


class LessonsLoader:
    def __init__(self, root_dir: Path, validator: LessonsContentValidator) -> None:
        self.root_dir = root_dir
        self.validator = validator

    def load(self) -> list[LoadedLesson]:
        index_path = self.root_dir / "index.yaml"
        index_payload = self._read_yaml(path=index_path)
        index_file = LessonsIndexFile.model_validate(obj=index_payload)
        self.validator.validate_index(index_file=index_file)

        lessons = []
        for index_item in index_file.lessons:
            lesson_dir = self._resolve_lesson_dir(slug=index_item.slug)
            lesson_meta = self._load_meta(lesson_dir=lesson_dir)
            lesson_cases = self._load_cases(lesson_dir=lesson_dir)
            lesson_quiz = self._load_quiz(lesson_dir=lesson_dir)
            theory = self._read_text(path=lesson_dir / LESSON_THEORY_FILENAME)
            starter_code = self._read_text(path=lesson_dir / LESSON_STARTER_FILENAME)
            lessons.append(
                LoadedLesson(
                    slug=index_item.slug,
                    order=index_item.order,
                    name=lesson_meta.title,
                    body_markdown=theory,
                    code_editor_default=starter_code,
                    cases=lesson_cases.cases,
                    questions=lesson_quiz.questions,
                    source_dir=lesson_dir,
                ),
            )

        lessons.sort(key=lambda item: lesson_order_key(item.order))
        return lessons

    def _resolve_lesson_dir(self, slug: str) -> Path:
        direct_path = self.root_dir / slug
        if direct_path.is_dir() and (direct_path / LESSON_META_FILENAME).exists():
            return direct_path

        candidates = [
            path.parent
            for path in self.root_dir.rglob(LESSON_META_FILENAME)
            if path.parent.name == slug
        ]

        if not candidates:
            raise FileNotFoundError(direct_path)

        if len(candidates) > 1:
            joined = ", ".join(str(path) for path in candidates)
            message = f"multiple lesson directories match slug '{slug}': {joined}"
            raise ValueError(message)

        return candidates[0]

    def _load_meta(self, lesson_dir: Path) -> LessonMetaFile:
        payload = self._read_yaml(path=lesson_dir / LESSON_META_FILENAME)
        return LessonMetaFile.model_validate(obj=payload)

    def _load_cases(self, lesson_dir: Path) -> LessonCasesFile:
        payload = self._read_yaml(path=lesson_dir / LESSON_CASES_FILENAME)
        raw_cases = payload.get("cases")
        if raw_cases is None:
            return LessonCasesFile(cases=[])
        return LessonCasesFile.model_validate(obj=payload)

    def _load_quiz(self, lesson_dir: Path) -> LessonQuizFile:
        payload = self._read_yaml(path=lesson_dir / LESSON_QUIZ_FILENAME)
        raw_questions = payload.get("questions")
        if raw_questions is None:
            return LessonQuizFile(questions=[])
        return LessonQuizFile.model_validate(obj=payload)

    @staticmethod
    def _read_yaml(path: Path) -> dict:
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
        if not path.exists():
            raise FileNotFoundError(path)

        return path.read_text(encoding="utf-8")
