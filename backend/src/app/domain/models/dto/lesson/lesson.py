from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LessonDTO(BaseModel):
    id: UUID
    order: int
    slug: str
    name: str
    body_markdown: str
    expected_output: str
    created_at: datetime
    updated_at: datetime | None
