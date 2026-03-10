from datetime import datetime

from pydantic import field_validator

from src.app.domain.lesson_order import normalize_lesson_order
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.case import LessonCaseDTO


class UpdateLessonDTO(ExtendedBaseModel):
    order: str | None = None
    slug: str | None = None
    name: str | None = None
    body_markdown: str | None = None
    code_editor_default: str | None = None
    cases: list[LessonCaseDTO] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("order", mode="before")
    @classmethod
    def validate_order(cls, value: str | int | float | None) -> str | None:
        if value is None:
            return None

        return normalize_lesson_order(value=value)

    @field_validator("name", "slug", "body_markdown")
    @classmethod
    def validate_non_blank(cls, value: str | None) -> str | None:

        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            message = "lesson text fields must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("cases")
    @classmethod
    def validate_unique_case_names(
            cls,
            cases: list[LessonCaseDTO] | None,
    ) -> list[LessonCaseDTO] | None:
        """
        Validate lesson case names are unique.

        :param cases: lesson cases

        :return: validated lesson cases
        """

        if cases is None:
            return None

        names = set()
        for case in cases:
            if case.name in names:
                message = f"Duplicate lesson case name: {case.name}"
                raise ValueError(message)
            names.add(case.name)

        return cases
