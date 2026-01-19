from pydantic import BaseModel


class LoginCredentials(BaseModel):
    username: str
    plain_password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
