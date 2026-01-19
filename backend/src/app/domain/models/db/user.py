from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.app.domain.models.db import Base
from backend.src.app.domain.models.dto.user import UserDTO


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    def to_dto(self) -> UserDTO:
        return UserDTO(
            id=self.id,
            username=self.username,
        )
