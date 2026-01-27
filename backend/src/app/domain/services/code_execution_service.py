import json
from uuid import UUID

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput, ExecutionPayloadTooLarge
from src.app.domain.models.dto.execution.execution_case import ExecutionCaseDTO
from src.app.domain.models.dto.execution.execution_result import ExecutionResultDTO
from src.app.domain.models.dto.lesson.lesson import LessonDTO
from src.app.domain.models.dto.lesson.sample_case import LessonSampleCaseDTO
from src.app.domain.models.enums.execution import ExecutionStatus
from src.app.domain.services.lesson_progress_service import LessonProgressService
from src.app.domain.services.lesson_service import LessonService
from src.app.domain.services.piston_service import PistonService
from src.app.eval.types import USER_CODE_PLACEHOLDER
from src.cfg.cfg import settings


class CodeExecutionService:
    def __init__(
            self,
            lesson_service: LessonService,
            piston_service: PistonService,
            progress_service: LessonProgressService,
    ) -> None:
        """
        Initialize code execution service.

        :param lesson_service: lesson service
        :param piston_service: piston service
        :param progress_service: progress service

        :return: None
        """
        self.lesson_service = lesson_service
        self.piston_service = piston_service
        self.progress_service = progress_service

    async def execute(self, lesson_id: UUID, code: str, user_id: UUID | None = None) -> ExecutionResultDTO:
        """
        Execute lesson code against evaluation script.

        :param lesson_id: lesson id
        :param code: user code
        :param user_id: user id

        :return: execution result
        """
        lesson = await self._get_lesson(lesson_id=lesson_id)
        self._validate_payload_sizes(
            code=code,
            eval_script=lesson.eval_script,
        )
        if not lesson.eval_script.strip():
            return ExecutionResultDTO(
                status=ExecutionStatus.RUNTIME_ERROR,
                cases=[],
                stderr="Evaluation script is not configured.",
                stdout=None,
                duration_ms=None,
            )
        if USER_CODE_PLACEHOLDER not in lesson.eval_script:
            return ExecutionResultDTO(
                status=ExecutionStatus.RUNTIME_ERROR,
                cases=[],
                stderr="Evaluation script is missing {{USER_CODE}} placeholder.",
                stdout=None,
                duration_ms=None,
            )

        source_code = self._render_source(
            definition_script=lesson.eval_script,
            code=code,
        )
        if len(source_code) > settings.execution.max_source_chars:
            raise ExecutionPayloadTooLarge
        try:
            piston_result = await self.piston_service.execute(source_code=source_code)
        except ExecutionInvalidOutput:
            return ExecutionResultDTO(
                status=ExecutionStatus.RUNTIME_ERROR,
                cases=[],
                stderr=None,
                stdout=None,
                duration_ms=None,
            )

        compile_result = piston_result.get("compile")
        if compile_result:
            compile_error = self._build_compile_error(compile_result=compile_result)
            if compile_error:
                return compile_error

        run_result = piston_result.get("run")
        if not run_result:
            raise ExecutionInvalidOutput

        run_error = self._build_run_error(run_result=run_result)
        if run_error:
            return run_error

        try:
            parsed = self._parse_stdout(stdout=run_result.get("stdout"))
            case_map = self._build_case_map(cases_payload=parsed.get("cases"))
        except ExecutionInvalidOutput:
            return ExecutionResultDTO(
                status=ExecutionStatus.RUNTIME_ERROR,
                cases=[],
                stderr=self._cap_output(
                    output=self._normalize_stderr(stderr=run_result.get("stderr")),
                ),
                stdout=self._cap_output(output=run_result.get("stdout")),
                duration_ms=run_result.get("wall_time"),
            )
        sample_cases = self._build_sample_cases(
            case_map=case_map,
            lesson_sample_cases=lesson.sample_cases,
        )
        status = ExecutionStatus.ACCEPTED if parsed.get("ok") is True else ExecutionStatus.WRONG_ANSWER

        if status == ExecutionStatus.ACCEPTED and user_id is not None:
            await self.progress_service.mark_completed(
                user_id=user_id,
                lesson_id=lesson_id,
            )

        return ExecutionResultDTO(
            status=status,
            cases=sample_cases,
            stderr=self._cap_output(
                output=self._normalize_stderr(stderr=run_result.get("stderr")),
            ),
            stdout=self._cap_output(output=run_result.get("stdout")),
            duration_ms=run_result.get("wall_time"),
        )

    async def _get_lesson(self, lesson_id: UUID) -> LessonDTO:
        """
        Resolve lesson data.

        :param lesson_id: lesson id

        :return: lesson dto
        """
        lesson = await self.lesson_service.get_by_id(id=lesson_id)
        return lesson

    @staticmethod
    def _render_source(definition_script: str, code: str) -> str:
        """
        Render full source code from template.

        :param definition_script: evaluation script template
        :param code: user code

        :return: merged source code
        """
        wrapped_code = CodeExecutionService._wrap_user_code(code=code)
        return definition_script.replace(USER_CODE_PLACEHOLDER, wrapped_code)

    @staticmethod
    def _wrap_user_code(code: str) -> str:
        """
        Wrap user code to surface runtime tracebacks.

        :param code: raw user code

        :return: wrapped user code
        """
        lines = code.splitlines()
        if not lines:
            return ""

        indented = "\n".join(f"    {line}" if line else "" for line in lines)
        return (
            "try:\n"
            f"{indented}\n"
            "except Exception:\n"
            "    raise\n"
        )

    @staticmethod
    def _build_compile_error(compile_result: dict) -> ExecutionResultDTO | None:
        """
        Build compile error result if compile failed.

        :param compile_result: piston compile result

        :return: error result or None
        """
        compile_status = compile_result.get("status")
        if compile_status not in ["TO", "SG"] and compile_result.get("code") in [0, None]:
            return None
        return ExecutionResultDTO(
            status=ExecutionStatus.COMPILE_ERROR,
            cases=[],
            stderr=CodeExecutionService._cap_output(
                output=CodeExecutionService._normalize_stderr(stderr=compile_result.get("stderr")),
            ),
            stdout=CodeExecutionService._cap_output(output=compile_result.get("stdout")),
            duration_ms=compile_result.get("wall_time"),
        )

    @staticmethod
    def _build_run_error(run_result: dict) -> ExecutionResultDTO | None:
        """
        Build run error result if runtime failed.

        :param run_result: piston run result

        :return: error result or None
        """
        run_status = run_result.get("status")
        if run_status == "TO":
            return ExecutionResultDTO(
                status=ExecutionStatus.TIMEOUT,
                cases=[],
                stderr=CodeExecutionService._cap_output(
                    output=CodeExecutionService._normalize_stderr(stderr=run_result.get("stderr")),
                ),
                stdout=CodeExecutionService._cap_output(output=run_result.get("stdout")),
                duration_ms=run_result.get("wall_time"),
            )
        if run_status not in ["SG", "RE"] and run_result.get("code") in [0, None]:
            return None
        return ExecutionResultDTO(
            status=ExecutionStatus.RUNTIME_ERROR,
            cases=[],
            stderr=CodeExecutionService._cap_output(
                output=CodeExecutionService._normalize_stderr(stderr=run_result.get("stderr")),
            ),
            stdout=CodeExecutionService._cap_output(output=run_result.get("stdout")),
            duration_ms=run_result.get("wall_time"),
        )

    @staticmethod
    def _normalize_stderr(stderr: str | None) -> str | None:
        """
        Normalize stderr by removing duplicated tracebacks.

        :param stderr: raw stderr output

        :return: normalized stderr output
        """
        if not stderr:
            return stderr
        trimmed = stderr.strip("\n")
        lines = trimmed.splitlines()
        if len(lines) % 2 == 0:
            half = len(lines) // 2
            if lines[:half] == lines[half:]:
                normalized = "\n".join(lines[:half])
                return f"{normalized}\n" if stderr.endswith("\n") else normalized
        return stderr

    @staticmethod
    def _cap_output(output: str | None) -> str | None:
        """
        Cap output size to prevent oversized payloads.

        :param output: raw output

        :return: capped output
        """
        if output is None:
            return None
        max_chars = settings.execution.max_output_chars
        if len(output) <= max_chars:
            return output
        suffix = "\n...[output truncated]"
        head = output[: max_chars - len(suffix)]
        return f"{head}{suffix}"

    @staticmethod
    def _validate_payload_sizes(code: str, eval_script: str) -> None:
        """
        Validate input sizes.

        :param code: user code
        :param eval_script: evaluation script

        :return: None
        """
        if len(code) > settings.execution.max_user_code_chars:
            raise ExecutionPayloadTooLarge
        if len(eval_script) > settings.execution.max_eval_script_chars:
            raise ExecutionPayloadTooLarge

    @staticmethod
    def _parse_stdout(stdout: str | None) -> dict:
        """
        Parse evaluator JSON output.

        :param stdout: run stdout

        :return: parsed payload
        """
        output = stdout or ""
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as exc:
            raise ExecutionInvalidOutput from exc
        if not isinstance(parsed, dict):
            raise ExecutionInvalidOutput
        return parsed

    @staticmethod
    def _build_case_map(cases_payload: object) -> dict:
        """
        Normalize cases payload into map.

        :param cases_payload: raw cases list

        :return: case map
        """
        if not isinstance(cases_payload, list):
            raise ExecutionInvalidOutput
        case_map = {}
        for case in cases_payload:
            if not isinstance(case, dict):
                continue
            name = case.get("name")
            if isinstance(name, str):
                case_map[name] = case
        return case_map

    @staticmethod
    def _build_sample_cases(
            case_map: dict,
            lesson_sample_cases: list[LessonSampleCaseDTO] | None,
    ) -> list[ExecutionCaseDTO]:
        """
        Build sample case DTOs.

        :param case_map: case results by name
        :param lesson_sample_cases: lesson-defined sample cases

        :return: sample case results
        """
        if not lesson_sample_cases:
            return []

        sample_cases = []
        for case in lesson_sample_cases:
            payload = case_map.get(case.name) or {}
            sample_cases.append(
                ExecutionCaseDTO(
                    name=case.name,
                    label=case.label,
                    ok=payload.get("ok") is True,
                    reason=payload.get("reason"),
                ),
            )
        return sample_cases
