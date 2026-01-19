from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.app.domain.models.db import Base
from backend.src.app.domain.models.dto.lesson import LessonDTO


class Lesson(Base):
    __tablename__ = "lessons"

    order: Mapped[int] = mapped_column(Integer())
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255), default="Lesson name")
    body_markdown: Mapped[str] = mapped_column(Text(), default="body")
    expected_output: Mapped[str] = mapped_column(Text())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dto(self) -> LessonDTO:
        """
        Convert model to DTO.

        :return: lesson dto
        """
        return LessonDTO.model_validate(obj=self, from_attributes=True)
