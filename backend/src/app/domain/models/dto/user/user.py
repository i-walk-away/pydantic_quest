from uuid import UUID

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class UserDTO(ExtendedBaseModel):
    id: UUID
    username: str
