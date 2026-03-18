from pydantic import Field, field_validator

from src.app.domain.lesson_order import normalize_lesson_order
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.case import LessonCaseDTO
from src.app.domain.models.dto.lesson.question import LessonQuestionDTO


class CreateLessonDTO(ExtendedBaseModel):
    name: str
    order: str
    slug: str
    body_markdown: str = Field(default="body")
    code_editor_default: str = Field(default="")
    cases: list[LessonCaseDTO] = Field(default_factory=list)
    questions: list[LessonQuestionDTO] = Field(default_factory=list)

    @field_validator("order", mode="before")
    @classmethod
    def validate_order(cls, value: str | int | float) -> str:
        return normalize_lesson_order(value=value)

    @field_validator("name", "slug", "body_markdown")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson text fields must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("cases")
    @classmethod
    def validate_unique_case_names(cls, cases: list[LessonCaseDTO]) -> list[LessonCaseDTO]:
        names = set()
        for case in cases:
            if case.name in names:
                message = f"Duplicate lesson case name: {case.name}"
                raise ValueError(message)
            names.add(case.name)

        return cases
