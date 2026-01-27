from pydantic import Field

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class UpdateUserDTO(ExtendedBaseModel):
    username: str | None = None
    email: str | None = None
    current_password: str | None = Field(default=None, exclude=True)
    new_password: str | None = Field(default=None, exclude=True)
