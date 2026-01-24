from datetime import datetime

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.sample_case import LessonSampleCaseDTO


class UpdateLessonDTO(ExtendedBaseModel):
    order: int | None = None
    slug: str | None = None
    name: str | None = None
    body_markdown: str | None = None
    expected_output: str | None = None
    code_editor_default: str | None = None
    eval_script: str | None = None
    sample_cases: list[LessonSampleCaseDTO] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
