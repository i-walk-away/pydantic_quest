from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from src.app.backend.models.db import Base
from src.app.backend.models.dto.lesson import LessonDTO


class Lesson(Base):
    __tablename__ = "lessons"

    slug: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column(default="Lesson name")
    body_markdown: Mapped[str] = mapped_column(default="body")
    expected_output: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(nullable=True)

    def to_dto(self) -> LessonDTO:
        return LessonDTO.model_validate(obj=self, from_attributes=True)
