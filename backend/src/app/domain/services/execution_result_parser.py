import json

from pydantic import ValidationError

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput
from src.app.domain.models.dto.execution.evaluator_output import (
    EvaluatorCaseOutputDTO,
    EvaluatorOutputDTO,
)
from src.app.domain.models.dto.execution.execution_case import ExecutionCaseDTO
from src.app.domain.models.dto.execution.execution_result import ExecutionResultDTO
from src.app.domain.models.dto.execution.runner_result import (
    RunnerExecutionResultDTO,
    RunnerStepResultDTO,
)
from src.app.domain.models.dto.lesson.case import LessonCaseDTO
from src.app.domain.models.enums.execution import ExecutionStatus


class ExecutionResultParser:
    def __init__(self, max_output_chars: int) -> None:
        """
        Initialize execution result parser.

        :param max_output_chars: max output size in characters

        :return: None
        """
        self.max_output_chars = max_output_chars

    def parse(
            self,
            runner_result: RunnerExecutionResultDTO,
            lesson_cases: list[LessonCaseDTO],
    ) -> ExecutionResultDTO:
        """
        Parse runner response into execution result.

        This method is the only place that translates low-level runner output
        into user-facing statuses and messages, so API behavior stays consistent.

        :param runner_result: runner response payload
        :param lesson_cases: lesson cases

        :return: execution result
        """
        if runner_result.compile is not None:
            compile_error = self._build_compile_error(compile_result=runner_result.compile)

            if compile_error is not None:
                return compile_error

        run_result = runner_result.run

        if run_result is None:
            raise ExecutionInvalidOutput

        run_error = self._build_run_error(run_result=run_result)

        if run_error is not None:
            return run_error

        evaluator_output = self._parse_evaluator_output(stdout=run_result.stdout)
        case_map = {case.name: case for case in evaluator_output.cases}
        sample_cases = self._build_sample_cases(
            case_map=case_map,
            lesson_cases=lesson_cases,
        )
        status = ExecutionStatus.ACCEPTED if evaluator_output.ok else ExecutionStatus.WRONG_ANSWER

        return ExecutionResultDTO(
            status=status,
            cases=sample_cases,
            stderr=self._cap_output(
                output=self._normalize_stderr(stderr=run_result.stderr),
            ),
            stdout=self._cap_output(output=run_result.stdout),
            duration_ms=run_result.wall_time,
        )

    def _build_compile_error(self, compile_result: RunnerStepResultDTO) -> ExecutionResultDTO | None:
        """
        Build compile error result.

        The parser treats empty compile stderr as infrastructure corruption,
        because the UI must always have concrete error text to display.

        :param compile_result: compile step result

        :return: compile error result or None
        """

        if compile_result.status not in ["TO", "SG"] and compile_result.code in [0, None]:
            return None

        stderr = self._cap_output(
            output=self._normalize_stderr(stderr=compile_result.stderr),
        )

        if not stderr:
            raise ExecutionInvalidOutput

        return ExecutionResultDTO(
            status=ExecutionStatus.COMPILE_ERROR,
            cases=[],
            stderr=stderr,
            stdout=self._cap_output(output=compile_result.stdout),
            duration_ms=compile_result.wall_time,
        )

    def _build_run_error(self, run_result: RunnerStepResultDTO) -> ExecutionResultDTO | None:
        """
        Build runtime error result.

        The parser treats empty runtime stderr as infrastructure corruption,
        because the UI must always have concrete error text to display.

        :param run_result: run step result

        :return: runtime error result or None
        """
        if run_result.status == "TO":
            stderr = self._cap_output(
                output=self._normalize_stderr(stderr=run_result.stderr),
            )

            if not stderr:
                raise ExecutionInvalidOutput

            return ExecutionResultDTO(
                status=ExecutionStatus.TIMEOUT,
                cases=[],
                stderr=stderr,
                stdout=self._cap_output(output=run_result.stdout),
                duration_ms=run_result.wall_time,
            )

        if run_result.status not in ["SG", "RE"] and run_result.code in [0, None]:
            return None

        stderr = self._cap_output(
            output=self._normalize_stderr(stderr=run_result.stderr),
        )

        if not stderr:
            raise ExecutionInvalidOutput

        return ExecutionResultDTO(
            status=ExecutionStatus.RUNTIME_ERROR,
            cases=[],
            stderr=stderr,
            stdout=self._cap_output(output=run_result.stdout),
            duration_ms=run_result.wall_time,
        )

    @staticmethod
    def _parse_evaluator_output(stdout: str | None) -> EvaluatorOutputDTO:
        """
        Parse evaluator JSON payload.

        Strict model validation is used here to fail fast when evaluator
        contracts drift, instead of silently returning partial results.

        :param stdout: evaluator stdout

        :return: evaluator output
        """
        output = stdout or ""
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as exc:
            raise ExecutionInvalidOutput from exc
        try:
            return EvaluatorOutputDTO.model_validate(obj=payload)
        except ValidationError as exc:
            raise ExecutionInvalidOutput from exc

    @staticmethod
    def _normalize_stderr(stderr: str | None) -> str | None:
        """
        Normalize stderr by removing duplicated tracebacks.

        Some execution environments duplicate traceback blocks, so this keeps
        the output readable without hiding actual error information.

        :param stderr: raw stderr output

        :return: normalized stderr
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

    def _cap_output(self, output: str | None) -> str | None:
        """
        Cap output size.

        This prevents oversized payloads from degrading API responses and UI rendering.

        :param output: raw output

        :return: capped output
        """

        if output is None:
            return None

        if len(output) <= self.max_output_chars:
            return output

        suffix = "\n...[output truncated]"
        head = output[: self.max_output_chars - len(suffix)]

        return f"{head}{suffix}"

    @staticmethod
    def _build_sample_cases(
            case_map: dict[str, EvaluatorCaseOutputDTO],
            lesson_cases: list[LessonCaseDTO],
    ) -> list[ExecutionCaseDTO]:
        """
        Build sample cases from evaluator output.

        Missing case results are converted into explicit failed sample cases
        to avoid silent pass conditions in the UI.

        :param case_map: map from case name to evaluator case payload
        :param lesson_cases: lesson cases

        :return: sample cases
        """
        sample_cases = []
        for case in lesson_cases:
            if case.hidden:
                continue
            evaluator_case = case_map.get(case.name)
            if evaluator_case is not None:
                sample_cases.append(
                    ExecutionCaseDTO(
                        name=case.name,
                        label=case.label,
                        ok=evaluator_case.ok,
                        reason=evaluator_case.reason,
                    ),
                )
                continue
            sample_cases.append(
                ExecutionCaseDTO(
                    name=case.name,
                    label=case.label,
                    ok=False,
                    reason="case result is missing",
                ),
            )

        return sample_cases
