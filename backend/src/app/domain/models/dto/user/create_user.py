from pydantic import Field

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CreateUserDTO(ExtendedBaseModel):
    username: str
    plain_password: str = Field(exclude=True)
