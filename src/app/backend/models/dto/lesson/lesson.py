from datetime import datetime

from pydantic import BaseModel


class LessonDTO(BaseModel):
    id: str
    slug: str
    name: str
    body_markdown: str
    expected_output: str
    created_at: datetime
    updated_at: datetime
