from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class GithubOAuthCallbackDTO(ExtendedBaseModel):
    """
    GitHub OAuth callback data.
    """
    code: str
    state: str

    @field_validator("code", "state")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "oauth callback fields must not be empty."
            raise ValueError(message)

        return normalized


class GithubTokenDTO(ExtendedBaseModel):
    """
    GitHub OAuth token response.
    """
    access_token: str
    token_type: str | None = None
    scope: str | None = None

    @field_validator("token_type", "scope")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class GithubUserDTO(ExtendedBaseModel):
    """
    GitHub user response payload.
    """
    id: int
    login: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "login must not be empty."
            raise ValueError(message)

        return normalized


class GithubEmailDTO(ExtendedBaseModel):
    """
    GitHub email response payload.
    """
    email: str
    primary: bool
    verified: bool

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip()
        if "@" not in normalized:
            message = "email must be a valid address."
            raise ValueError(message)

        return normalized
