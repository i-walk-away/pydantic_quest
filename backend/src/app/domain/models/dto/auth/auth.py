from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LoginCredentials(ExtendedBaseModel):
    username: str
    plain_password: str


class LoginResponse(ExtendedBaseModel):
    access_token: str
    token_type: str = 'bearer'
