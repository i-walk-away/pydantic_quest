import json
from uuid import UUID

from src.app.core.exceptions.execution_exc import ExecutionPayloadTooLarge
from src.app.domain.models.dto.execution.execution_result import ExecutionResultDTO
from src.app.domain.models.dto.lesson.case import LessonCaseDTO
from src.app.domain.models.dto.lesson.lesson import LessonDTO
from src.app.domain.models.enums.execution import ExecutionStatus
from src.app.domain.services.code_runner import CodeRunner
from src.app.domain.services.execution_result_parser import ExecutionResultParser
from src.app.domain.services.execution_source_builder import ExecutionSourceBuilder
from src.app.domain.services.lesson_progress_service import LessonProgressService
from src.app.domain.services.lesson_service import LessonService
from src.cfg.cfg import settings


class CodeExecutionService:
    def __init__(
            self,
            lesson_service: LessonService,
            code_runner: CodeRunner,
            progress_service: LessonProgressService,
            source_builder: ExecutionSourceBuilder,
            result_parser: ExecutionResultParser,
    ) -> None:
        self.lesson_service = lesson_service
        self.code_runner = code_runner
        self.progress_service = progress_service
        self.source_builder = source_builder
        self.result_parser = result_parser

    async def execute(self, lesson_id: UUID, code: str, user_id: UUID | None = None) -> ExecutionResultDTO:
        lesson = await self._get_lesson(lesson_id=lesson_id)
        self._validate_payload_sizes(code=code, cases=lesson.cases)

        if not lesson.cases:
            return ExecutionResultDTO(
                status=ExecutionStatus.RUNTIME_ERROR,
                cases=[],
                stderr="This lesson does not have a coding task.",
                stdout=None,
                duration_ms=None,
            )

        source_code = self.source_builder.build(cases=lesson.cases, code=code)
        if len(source_code) > settings.execution.max_source_chars:
            raise ExecutionPayloadTooLarge

        runner_result = await self.code_runner.execute(source_code=source_code)
        result = self.result_parser.parse(runner_result=runner_result, lesson_cases=lesson.cases)

        if result.status == ExecutionStatus.ACCEPTED and user_id is not None:
            await self.progress_service.mark_completed(user_id=user_id, lesson_id=lesson_id)

        return result

    async def _get_lesson(self, lesson_id: UUID) -> LessonDTO:
        return await self.lesson_service.get_by_id(id=lesson_id)

    @staticmethod
    def _validate_payload_sizes(code: str, cases: list[LessonCaseDTO]) -> None:
        if len(code) > settings.execution.max_user_code_chars:
            raise ExecutionPayloadTooLarge

        cases_json = json.dumps([case.model_dump() for case in cases])
        if len(cases_json) > settings.execution.max_eval_script_chars:
            raise ExecutionPayloadTooLarge
