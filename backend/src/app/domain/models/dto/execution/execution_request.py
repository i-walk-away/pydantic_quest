from uuid import UUID

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class ExecutionRequestDTO(ExtendedBaseModel):
    lesson_id: UUID
    code: str
