from pydantic import field_validator

from src.app.domain.models.dto.execution.execution_case import ExecutionCaseDTO
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.enums.execution import ExecutionStatus


class ExecutionResultDTO(ExtendedBaseModel):
    status: ExecutionStatus
    cases: list[ExecutionCaseDTO]
    stderr: str | None = None
    stdout: str | None = None
    duration_ms: int | None = None

    @field_validator("duration_ms")
    @classmethod
    def validate_duration_ms(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            message = "duration_ms must be non-negative."
            raise ValueError(message)

        return value
