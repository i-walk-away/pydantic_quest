from __future__ import annotations

from pathlib import Path

from pydantic import ConfigDict, field_validator, model_validator

from src.app.domain.lesson_order import normalize_lesson_order
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LessonIndexItem(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    order: str

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "slug must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("order", mode="before")
    @classmethod
    def validate_order(cls, value: str | int | float) -> str:
        return normalize_lesson_order(value=value)


class LessonsIndexFile(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    lessons: list[LessonIndexItem]

    @field_validator("lessons")
    @classmethod
    def validate_lessons_not_empty(cls, value: list[LessonIndexItem]) -> list[LessonIndexItem]:
        if not value:
            message = "lessons index must contain at least one lesson."
            raise ValueError(message)

        return value


class LessonMetaFile(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str

    @field_validator("title")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson metadata text fields must not be empty."
            raise ValueError(message)

        return normalized


class LessonCaseFileItem(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    label: str
    script: str
    hidden: bool = False

    @field_validator("name", "label", "script")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson case fields must not be empty."
            raise ValueError(message)

        return normalized


class LessonCasesFile(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    cases: list[LessonCaseFileItem]

    @model_validator(mode="after")
    def validate_unique_case_names(self) -> LessonCasesFile:
        names = set()
        for case in self.cases:
            if case.name in names:
                message = f"Duplicate lesson case name: {case.name}"
                raise ValueError(message)
            names.add(case.name)

        return self


class LoadedLesson(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    order: str
    name: str
    body_markdown: str
    code_editor_default: str
    cases: list[LessonCaseFileItem]
    source_dir: Path

    @field_validator("order", mode="before")
    @classmethod
    def validate_order(cls, value: str | int | float) -> str:
        return normalize_lesson_order(value=value)

    @field_validator("slug", "name", "body_markdown")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "loaded lesson text fields must not be empty."
            raise ValueError(message)

        return normalized
