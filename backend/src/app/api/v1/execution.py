from fastapi import APIRouter, Depends

from src.app.core.dependencies.security.execution import enforce_execution_rate_limit
from src.app.core.dependencies.services.code_execution import get_code_execution_service
from src.app.domain.models.dto.execution.execution_request import ExecutionRequestDTO
from src.app.domain.models.dto.execution.execution_result import ExecutionResultDTO
from src.app.domain.services.code_execution_service import CodeExecutionService

router = APIRouter(
    prefix="/execute",
    tags=["Execution"],
    dependencies=[Depends(enforce_execution_rate_limit)],
)


@router.post(path="/run", summary="Run lesson code")
async def run_lesson_code(
        data: ExecutionRequestDTO,
        code_execution_service: CodeExecutionService = Depends(get_code_execution_service),
) -> ExecutionResultDTO:
    """
    Execute lesson code against evaluation script.

    :param data: execution request data
    :param code_execution_service: code execution service

    :return: execution result
    """
    return await code_execution_service.execute(lesson_id=data.lesson_id, code=data.code)
