from pydantic import Field

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CreateLessonDTO(ExtendedBaseModel):
    name: str
    order: int
    slug: str
    body_markdown: str = Field(default='body')
    expected_output: str
