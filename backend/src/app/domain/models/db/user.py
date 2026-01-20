from sqlalchemy import Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.domain.models.db import Base
from src.app.domain.models.dto.user import UserDTO
from src.app.domain.models.enums.role import UserRole


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        default=UserRole.USER
    )

    def to_dto(self) -> UserDTO:
        return UserDTO.model_validate(obj=self, from_attributes=True)
