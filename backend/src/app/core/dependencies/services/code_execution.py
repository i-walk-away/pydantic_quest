from pathlib import Path

from fastapi import Depends

from src.app.core.dependencies.services.lesson import get_lesson_service
from src.app.core.dependencies.services.lesson_progress import get_lesson_progress_service
from src.app.core.dependencies.services.piston import get_piston_service
from src.app.domain.services.code_execution_service import CodeExecutionService
from src.app.domain.services.code_runner import CodeRunner
from src.app.domain.services.execution_result_parser import ExecutionResultParser
from src.app.domain.services.execution_source_builder import ExecutionSourceBuilder
from src.app.domain.services.lesson_progress_service import LessonProgressService
from src.app.domain.services.lesson_service import LessonService
from src.cfg.cfg import settings

EVAL_RUNNER_TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "eval" / "runtime_runner.py.tpl"
SOURCE_BUILDER = ExecutionSourceBuilder.from_template_file(path=EVAL_RUNNER_TEMPLATE_PATH)
RESULT_PARSER = ExecutionResultParser(max_output_chars=settings.execution.max_output_chars)


def get_code_execution_service(
        lesson_service: LessonService = Depends(get_lesson_service),
        code_runner: CodeRunner = Depends(get_piston_service),
        progress_service: LessonProgressService = Depends(get_lesson_progress_service),
) -> CodeExecutionService:
    """
    Build code execution service.

    :param lesson_service: lesson service
    :param code_runner: code runner
    :param progress_service: progress service

    :return: code execution service
    """

    return CodeExecutionService(
        lesson_service=lesson_service,
        code_runner=code_runner,
        progress_service=progress_service,
        source_builder=SOURCE_BUILDER,
        result_parser=RESULT_PARSER,
    )
