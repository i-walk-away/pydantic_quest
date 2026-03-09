from pydantic import Field, field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CreateUserDTO(ExtendedBaseModel):
    username: str
    plain_password: str = Field(exclude=True)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "username must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("plain_password")
    @classmethod
    def validate_plain_password(cls, value: str) -> str:
        if not value:
            message = "plain_password must not be empty."
            raise ValueError(message)

        return value
