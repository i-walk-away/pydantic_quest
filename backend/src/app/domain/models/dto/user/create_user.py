from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    username: str
    plain_password: str
