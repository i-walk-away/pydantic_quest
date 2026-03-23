from __future__ import annotations

from pathlib import Path

from pydantic import ConfigDict, Field, field_validator, model_validator

from src.app.domain.lesson_order import normalize_lesson_order
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


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

    cases: list[LessonCaseFileItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_case_names(self) -> LessonCasesFile:
        names = set()
        for case in self.cases:
            if case.name in names:
                message = f"Duplicate lesson case name: {case.name}"
                raise ValueError(message)
            names.add(case.name)

        return self


class LessonQuizQuestionFileItem(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    options: list[str]
    correct_option: int

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson quiz question prompt must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        if len(value) < 2:
            message = "lesson quiz question must have at least two options."
            raise ValueError(message)

        normalized_options = []
        for option in value:
            normalized = option.strip()
            if not normalized:
                message = "lesson quiz options must not be empty."
                raise ValueError(message)
            normalized_options.append(normalized)

        return normalized_options

    @model_validator(mode="after")
    def validate_correct_option(self) -> LessonQuizQuestionFileItem:
        if self.correct_option < 0 or self.correct_option >= len(self.options):
            message = "lesson quiz correct_option must point to an existing option."
            raise ValueError(message)

        return self


class LessonQuizFile(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[LessonQuizQuestionFileItem] = Field(default_factory=list)


class LoadedLesson(ExtendedBaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    order: str
    name: str
    body_markdown: str
    code_editor_default: str
    cases: list[LessonCaseFileItem]
    questions: list[LessonQuizQuestionFileItem]
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
