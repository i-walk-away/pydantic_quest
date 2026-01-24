from datetime import datetime
from uuid import UUID

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.sample_case import LessonSampleCaseDTO


class LessonDTO(ExtendedBaseModel):
    id: UUID
    order: int
    slug: str
    name: str
    body_markdown: str
    expected_output: str
    code_editor_default: str
    eval_script: str
    sample_cases: list[LessonSampleCaseDTO] | None = None
    created_at: datetime
    updated_at: datetime | None
