import re
from pathlib import Path

import yaml

from src.app.content.models import LessonCasesFile, LessonMetaFile, LessonQuizFile, LoadedLesson
from src.app.content.validator import LessonsContentValidator
from src.app.domain.lesson_order import lesson_order_key

LESSON_META_FILENAME = "lesson.yaml"
LESSON_THEORY_FILENAME = "theory.md"
LESSON_STARTER_FILENAME = "starter.py"
LESSON_CASES_FILENAME = "cases.yaml"
LESSON_QUIZ_FILENAME = "quiz.yaml"
LESSON_TEMPLATE_DIRNAME = "lesson-template"
LESSON_DIR_PATTERN = re.compile(r"^(?P<prefix>\d+)-(?P<slug>[a-z0-9][a-z0-9-]*)$")


class LessonsLoader:
    def __init__(self, root_dir: Path, validator: LessonsContentValidator) -> None:
        self.root_dir = root_dir
        self.validator = validator

    def load(self) -> list[LoadedLesson]:
        lessons = []
        for lesson_dir in self._discover_lesson_dirs():
            slug, order = self._infer_slug_and_order(lesson_dir=lesson_dir)
            lesson_meta = self._load_meta(lesson_dir=lesson_dir)
            lesson_cases = self._load_cases(lesson_dir=lesson_dir)
            lesson_quiz = self._load_quiz(lesson_dir=lesson_dir)
            theory = self._read_text(path=lesson_dir / LESSON_THEORY_FILENAME)
            starter_code = self._read_text(path=lesson_dir / LESSON_STARTER_FILENAME)
            lessons.append(
                LoadedLesson(
                    slug=slug,
                    order=order,
                    name=lesson_meta.title,
                    body_markdown=theory,
                    code_editor_default=starter_code,
                    cases=lesson_cases.cases,
                    questions=lesson_quiz.questions,
                    source_dir=lesson_dir,
                ),
            )

        self.validator.validate_lessons(lessons=lessons)
        lessons.sort(key=lambda item: lesson_order_key(item.order))
        return lessons

    def _discover_lesson_dirs(self) -> list[Path]:
        lesson_dirs = []
        for meta_path in self.root_dir.rglob(LESSON_META_FILENAME):
            lesson_dir = meta_path.parent
            if lesson_dir.name == LESSON_TEMPLATE_DIRNAME:
                continue
            self._infer_slug_and_order(lesson_dir=lesson_dir)
            lesson_dirs.append(lesson_dir)

        return lesson_dirs

    def _infer_slug_and_order(self, lesson_dir: Path) -> tuple[str, str]:
        relative_parts = lesson_dir.relative_to(self.root_dir).parts
        if not relative_parts:
            message = f"lesson directory cannot be the root lessons directory: {lesson_dir}"
            raise ValueError(message)

        order_segments: list[str] = []
        slug = ""

        for part in relative_parts:
            match = LESSON_DIR_PATTERN.fullmatch(part)
            if match is None:
                message = (
                    "lesson directory name must start with a numeric prefix like "
                    f"'01-my-lesson': {lesson_dir}"
                )
                raise ValueError(message)

            order_segments.append(str(int(match.group("prefix"))))
            slug = match.group("slug")

        return slug, ".".join(order_segments)

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
