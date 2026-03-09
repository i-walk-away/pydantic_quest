import json

import pytest

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput
from src.app.domain.models.dto.execution.runner_result import RunnerExecutionResultDTO
from src.app.domain.models.dto.lesson.case import LessonCaseDTO
from src.app.domain.models.enums.execution import ExecutionStatus
from src.app.domain.services.execution_result_parser import ExecutionResultParser


def _lesson_cases() -> list[LessonCaseDTO]:
    return [
        LessonCaseDTO(
            name="case_1",
            label="case 1",
            script="ok = True",
            hidden=False,
        ),
    ]


def test_parse_compile_error_with_empty_stderr_raises_invalid_output() -> None:
    parser = ExecutionResultParser(max_output_chars=100)
    runner_result = RunnerExecutionResultDTO.model_validate(
        obj={
            "compile": {
                "status": "SG",
                "code": None,
                "stdout": "",
                "stderr": "",
                "wall_time": 1,
            },
        },
    )

    with pytest.raises(ExecutionInvalidOutput):
        parser.parse(
            runner_result=runner_result,
            lesson_cases=_lesson_cases(),
        )


def test_parse_runtime_error_with_empty_stderr_raises_invalid_output() -> None:
    parser = ExecutionResultParser(max_output_chars=100)
    runner_result = RunnerExecutionResultDTO.model_validate(
        obj={
            "run": {
                "status": "RE",
                "code": 1,
                "stdout": "",
                "stderr": "",
                "wall_time": 1,
            },
        },
    )

    with pytest.raises(ExecutionInvalidOutput):
        parser.parse(
            runner_result=runner_result,
            lesson_cases=_lesson_cases(),
        )


def test_parse_normalizes_duplicated_traceback_stderr() -> None:
    parser = ExecutionResultParser(max_output_chars=500)
    evaluator_payload = {
        "ok": True,
        "cases": [{"name": "case_1", "ok": True}],
    }
    duplicated = "Traceback line 1\nTraceback line 2\nTraceback line 1\nTraceback line 2\n"
    runner_result = RunnerExecutionResultDTO.model_validate(
        obj={
            "run": {
                "status": None,
                "code": 0,
                "stdout": json.dumps(evaluator_payload),
                "stderr": duplicated,
                "wall_time": 1,
            },
        },
    )

    result = parser.parse(
        runner_result=runner_result,
        lesson_cases=_lesson_cases(),
    )

    assert result.status == ExecutionStatus.ACCEPTED
    assert result.stderr == "Traceback line 1\nTraceback line 2\n"


def test_parse_adds_missing_case_result_as_failure() -> None:
    parser = ExecutionResultParser(max_output_chars=500)
    evaluator_payload = {
        "ok": False,
        "cases": [],
    }
    runner_result = RunnerExecutionResultDTO.model_validate(
        obj={
            "run": {
                "status": None,
                "code": 0,
                "stdout": json.dumps(evaluator_payload),
                "stderr": "",
                "wall_time": 1,
            },
        },
    )

    result = parser.parse(
        runner_result=runner_result,
        lesson_cases=_lesson_cases(),
    )

    assert result.status == ExecutionStatus.WRONG_ANSWER
    assert result.cases[0].ok is False
    assert result.cases[0].reason == "case result is missing"


def test_parse_caps_output() -> None:
    parser = ExecutionResultParser(max_output_chars=25)
    long_stderr = "0123456789abcdefghij0123456789"
    runner_result = RunnerExecutionResultDTO.model_validate(
        obj={
            "run": {
                "status": "RE",
                "code": 1,
                "stdout": "",
                "stderr": long_stderr,
                "wall_time": 1,
            },
        },
    )

    result = parser.parse(
        runner_result=runner_result,
        lesson_cases=_lesson_cases(),
    )

    assert result.status == ExecutionStatus.RUNTIME_ERROR
    assert result.stderr is not None
    assert result.stderr.endswith("...[output truncated]")
