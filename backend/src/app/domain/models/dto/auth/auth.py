from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LoginCredentials(ExtendedBaseModel):
    username: str
    plain_password: str

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


class LoginResponse(ExtendedBaseModel):
    access_token: str
    token_type: str = 'bearer'

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, value: str) -> str:
        if not value.strip():
            message = "access_token must not be empty."
            raise ValueError(message)

        return value

    @field_validator("token_type")
    @classmethod
    def validate_token_type(cls, value: str) -> str:
        normalized = value.strip().lower()

        if not normalized:
            message = "token_type must not be empty."
            raise ValueError(message)

        return normalized
