from pydantic import BaseModel, Field


class CreateLessonDTO(BaseModel):
    name: str
    order: int
    slug: str
    body_markdown: str = Field(default='body')
    expected_output: str
