from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column

from src.app.backend.models.db import Base
from src.app.backend.models.dto.lesson import LessonDTO


class Lesson(Base):
    __tablename__ = "lessons"
    dto_class = LessonDTO

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column(default="Lesson name")
    body_markdown: Mapped[str] = mapped_column(default="body")
    expected_output: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
