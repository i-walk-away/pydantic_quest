from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.app.domain.models.db import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey("lessons.id"), index=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
    )
