from pydantic import Field

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.sample_case import LessonSampleCaseDTO


class CreateLessonDTO(ExtendedBaseModel):
    name: str
    order: int
    slug: str
    body_markdown: str = Field(default='body')
    code_editor_default: str = Field(default="")
    eval_script: str = Field(default="")
    sample_cases: list[LessonSampleCaseDTO] | None = None
