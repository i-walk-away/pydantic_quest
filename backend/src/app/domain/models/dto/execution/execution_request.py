from uuid import UUID

from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class ExecutionRequestDTO(ExtendedBaseModel):
    lesson_id: UUID
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.strip():
            message = "code must not be empty."
            raise ValueError(message)

        return value
