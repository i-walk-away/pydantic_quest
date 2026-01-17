from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UpdateLessonDTO(BaseModel):
    id: UUID
    slug: str | None = None
    name: str | None = None
    body_markdown: str | None = None
    expected_output: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
