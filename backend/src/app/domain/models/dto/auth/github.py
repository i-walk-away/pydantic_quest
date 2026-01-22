from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class GithubOAuthCallbackDTO(ExtendedBaseModel):
    """
    GitHub OAuth callback data.
    """
    code: str
    state: str


class GithubTokenDTO(ExtendedBaseModel):
    """
    GitHub OAuth token response.
    """
    access_token: str
    token_type: str | None = None
    scope: str | None = None


class GithubUserDTO(ExtendedBaseModel):
    """
    GitHub user response payload.
    """
    id: int
    login: str


class GithubEmailDTO(ExtendedBaseModel):
    """
    GitHub email response payload.
    """
    email: str
    primary: bool
    verified: bool
