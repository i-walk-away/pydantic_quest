from fastapi import Depends

from src.app.core.dependencies.services.lesson import get_lesson_service
from src.app.core.dependencies.services.lesson_progress import get_lesson_progress_service
from src.app.core.dependencies.services.piston import get_piston_service
from src.app.domain.services.code_execution_service import CodeExecutionService
from src.app.domain.services.lesson_progress_service import LessonProgressService
from src.app.domain.services.lesson_service import LessonService
from src.app.domain.services.piston_service import PistonService


def get_code_execution_service(
        lesson_service: LessonService = Depends(get_lesson_service),
        piston_service: PistonService = Depends(get_piston_service),
        progress_service: LessonProgressService = Depends(get_lesson_progress_service),
) -> CodeExecutionService:
    """
    Build code execution service.

    :param lesson_service: lesson service
    :param piston_service: piston service
    :param progress_service: progress service

    :return: code execution service
    """
    return CodeExecutionService(
        lesson_service=lesson_service,
        piston_service=piston_service,
        progress_service=progress_service,
    )
