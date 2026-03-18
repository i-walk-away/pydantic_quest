from datetime import datetime
from uuid import UUID

from pydantic import computed_field, field_validator

from src.app.domain.lesson_order import normalize_lesson_order
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.case import LessonCaseDTO
from src.app.domain.models.dto.lesson.question import LessonQuestionDTO
from src.app.domain.models.dto.lesson.sample_case import LessonSampleCaseDTO


class LessonDTO(ExtendedBaseModel):
    id: UUID
    order: str
    slug: str
    name: str
    body_markdown: str
    code_editor_default: str
    cases: list[LessonCaseDTO]
    questions: list[LessonQuestionDTO]
    sample_cases: list[LessonSampleCaseDTO] | None = None
    created_at: datetime
    updated_at: datetime | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def no_code(self) -> bool:
        return len(self.cases) == 0

    @field_validator("order", mode="before")
    @classmethod
    def validate_order(cls, value: str | int | float) -> str:
        return normalize_lesson_order(value=value)

    @field_validator("slug", "name", "body_markdown")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson text fields must not be empty."
            raise ValueError(message)

        return normalized
