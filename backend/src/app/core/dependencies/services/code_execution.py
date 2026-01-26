from fastapi import Depends

from src.app.core.dependencies.services.lesson import get_lesson_service
from src.app.core.dependencies.services.piston import get_piston_service
from src.app.domain.services.code_execution_service import CodeExecutionService
from src.app.domain.services.lesson_service import LessonService
from src.app.domain.services.piston_service import PistonService


def get_code_execution_service(
        lesson_service: LessonService = Depends(get_lesson_service),
        piston_service: PistonService = Depends(get_piston_service),
) -> CodeExecutionService:
    """
    Build code execution service.

    :param lesson_service: lesson service
    :param piston_service: piston service

    :return: code execution service
    """
    return CodeExecutionService(
        lesson_service=lesson_service,
        piston_service=piston_service,
    )
