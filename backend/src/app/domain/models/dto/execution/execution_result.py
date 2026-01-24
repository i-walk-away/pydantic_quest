from src.app.domain.models.dto.execution.execution_case import ExecutionCaseDTO
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.enums.execution import ExecutionStatus


class ExecutionResultDTO(ExtendedBaseModel):
    status: ExecutionStatus
    cases: list[ExecutionCaseDTO]
    stderr: str | None = None
    stdout: str | None = None
    duration_ms: int | None = None
