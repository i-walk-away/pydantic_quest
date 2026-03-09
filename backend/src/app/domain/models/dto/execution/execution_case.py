from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class ExecutionCaseDTO(ExtendedBaseModel):
    name: str
    label: str
    ok: bool
    reason: str | None = None

    @field_validator("name", "label")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "execution case fields must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None
