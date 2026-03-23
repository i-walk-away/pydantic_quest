from pydantic import field_validator, model_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LessonQuestionDTO(ExtendedBaseModel):
    prompt: str
    options: list[str]
    correct_option: int

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson question prompt must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        if len(value) < 2:
            message = "lesson question must have at least two options."
            raise ValueError(message)

        normalized_options = []
        for option in value:
            normalized = option.strip()
            if not normalized:
                message = "lesson question options must not be empty."
                raise ValueError(message)
            normalized_options.append(normalized)

        return normalized_options

    @model_validator(mode="after")
    def validate_correct_option(self) -> "LessonQuestionDTO":
        if self.correct_option < 0 or self.correct_option >= len(self.options):
            message = "lesson question correct_option must point to an existing option."
            raise ValueError(message)

        return self
