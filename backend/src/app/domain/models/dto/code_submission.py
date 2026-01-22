from pydantic import Field

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CodeSubmissionDTO(ExtendedBaseModel):
    code: str = Field(min_length=1)
