from fastapi import APIRouter, Depends

from src.app.core.dependencies.security.execution import enforce_execution_rate_limit
from src.app.core.dependencies.security.user import get_optional_user_from_jwt
from src.app.core.dependencies.services.code_analysis import get_code_analysis_service
from src.app.core.dependencies.services.code_execution import get_code_execution_service
from src.app.domain.models.dto.execution.code_analysis_request import (
    CodeAnalysisRequestDTO,
)
from src.app.domain.models.dto.execution.code_analysis_result import CodeAnalysisResultDTO
from src.app.domain.models.dto.execution.execution_request import ExecutionRequestDTO
from src.app.domain.models.dto.execution.execution_result import ExecutionResultDTO
from src.app.domain.models.dto.user.user import UserDTO
from src.app.domain.services.code_analysis_service import CodeAnalysisService
from src.app.domain.services.code_execution_service import CodeExecutionService

router = APIRouter(
    prefix="/execute",
    tags=["Execution"],
)


@router.post(path="/run", summary="Run lesson code")
async def run_lesson_code(
        data: ExecutionRequestDTO,
        _: None = Depends(enforce_execution_rate_limit),
        code_execution_service: CodeExecutionService = Depends(get_code_execution_service),
        user: UserDTO | None = Depends(get_optional_user_from_jwt),
) -> ExecutionResultDTO:
    """
    Execute lesson code against evaluation script.

    :param data: execution request data
    :param code_execution_service: code execution service

    :return: execution result
    """

    return await code_execution_service.execute(
        lesson_id=data.lesson_id,
        code=data.code,
        user_id=user.id if user else None,
    )


@router.post(path="/analyze", summary="Analyze lesson code")
async def analyze_lesson_code(
        data: CodeAnalysisRequestDTO,
        code_analysis_service: CodeAnalysisService = Depends(get_code_analysis_service),
) -> CodeAnalysisResultDTO:
    return await code_analysis_service.analyze(code=data.code)
