from datetime import datetime
from uuid import UUID

from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.case import LessonCaseDTO
from src.app.domain.models.dto.lesson.sample_case import LessonSampleCaseDTO


class LessonDTO(ExtendedBaseModel):
    id: UUID
    order: int
    slug: str
    name: str
    body_markdown: str
    code_editor_default: str
    cases: list[LessonCaseDTO]
    sample_cases: list[LessonSampleCaseDTO] | None = None
    created_at: datetime
    updated_at: datetime | None

    @field_validator("order")
    @classmethod
    def validate_order(cls, value: int) -> int:
        if value < 1:
            message = "order must be positive."
            raise ValueError(message)

        return value

    @field_validator("slug", "name", "body_markdown")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson text fields must not be empty."
            raise ValueError(message)

        return normalized
