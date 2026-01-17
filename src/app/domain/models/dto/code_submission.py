from pydantic import BaseModel, Field


class CodeSubmissionDTO(BaseModel):
    code: str = Field(min_length=5)
