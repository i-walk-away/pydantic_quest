from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LessonSampleCaseDTO(ExtendedBaseModel):
    name: str
    label: str

    @field_validator("name", "label")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "lesson sample case fields must not be empty."
            raise ValueError(message)

        return normalized
