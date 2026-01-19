from uuid import UUID

from pydantic import BaseModel


class UserDTO(BaseModel):
    id: UUID
    username: str
