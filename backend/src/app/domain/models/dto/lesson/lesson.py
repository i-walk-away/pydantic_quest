from datetime import datetime
from uuid import UUID

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LessonDTO(ExtendedBaseModel):
    id: UUID
    order: int
    slug: str
    name: str
    body_markdown: str
    expected_output: str
    code_editor_default: str
    created_at: datetime
    updated_at: datetime | None
