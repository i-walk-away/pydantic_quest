from uuid import UUID

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.enums.role import UserRole


class UserDTO(ExtendedBaseModel):
    id: UUID
    username: str
    email: str | None = None
    role: UserRole
