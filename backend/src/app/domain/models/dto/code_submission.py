from pydantic import Field, field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CodeSubmissionDTO(ExtendedBaseModel):
    code: str = Field(min_length=1)

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.strip():
            message = "code must not be empty."
            raise ValueError(message)

        return value
