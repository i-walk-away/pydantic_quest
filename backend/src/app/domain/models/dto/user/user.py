from uuid import UUID

from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.enums.role import UserRole


class UserDTO(ExtendedBaseModel):
    id: UUID
    username: str
    email: str | None = None
    role: UserRole

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "username must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:

        if value is None:
            return None

        normalized = value.strip()
        if "@" not in normalized:
            message = "email must be a valid address."
            raise ValueError(message)

        return normalized
