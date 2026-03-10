import json

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from src.app.core.dependencies.services.code_analysis import get_code_analysis_service
from src.app.core.dependencies.services.execution_rate_limiter import (
    get_execution_rate_limiter,
)
from src.app.core.dependencies.services.piston import get_piston_service
from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.dto.execution.code_analysis_result import CodeAnalysisResultDTO
from src.app.domain.models.dto.execution.runner_result import RunnerExecutionResultDTO
from src.app.domain.services.execution_rate_limiter import ExecutionRateLimiter

CASES = [
    {
        "name": "valid_create",
        "label": "valid create",
        "script": "ok = True",
        "hidden": False,
    },
    {
        "name": "invalid_age",
        "label": "invalid age",
        "script": "ok = True",
        "hidden": False,
    },
]


class FakePistonService:
    @staticmethod
    async def execute(*, source_code: str) -> RunnerExecutionResultDTO:
        _ = source_code
        payload = {
            "ok": True,
            "cases": [
                {"name": "valid_create", "ok": True},
                {"name": "invalid_age", "ok": True},
            ],
        }

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "run": {
                    "stdout": json.dumps(payload),
                    "stderr": "",
                    "status": None,
                    "code": 0,
                    "wall_time": 5,
                },
            },
        )


class FakePistonServiceInvalidOutput:
    @staticmethod
    async def execute(*, source_code: str) -> RunnerExecutionResultDTO:
        _ = source_code

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "run": {
                    "stdout": "not-json",
                    "stderr": "",
                    "status": None,
                    "code": 0,
                    "wall_time": 5,
                },
            },
        )


class FakePistonServiceWrongAnswer:
    @staticmethod
    async def execute(*, source_code: str) -> RunnerExecutionResultDTO:
        _ = source_code
        payload = {
            "ok": False,
            "cases": [
                {"name": "valid_create", "ok": False, "reason": "missing field"},
                {"name": "invalid_age", "ok": True},
            ],
        }

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "run": {
                    "stdout": json.dumps(payload),
                    "stderr": "",
                    "status": None,
                    "code": 0,
                    "wall_time": 5,
                },
            },
        )


class FakePistonServiceRuntimeError:
    @staticmethod
    async def execute(*, source_code: str) -> RunnerExecutionResultDTO:
        _ = source_code

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "run": {
                    "stdout": "",
                    "stderr": "boom",
                    "status": "RE",
                    "code": 1,
                    "wall_time": 5,
                },
            },
        )


class FakePistonServiceRuntimeErrorEmptyStderr:
    @staticmethod
    async def execute(*, source_code: str) -> RunnerExecutionResultDTO:
        _ = source_code

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "run": {
                    "stdout": "",
                    "stderr": "",
                    "status": "RE",
                    "code": 1,
                    "wall_time": 5,
                },
            },
        )


class FakePistonServiceCompileError:
    @staticmethod
    async def execute(*, source_code: str) -> RunnerExecutionResultDTO:
        _ = source_code

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "compile": {
                    "stdout": "",
                    "stderr": "compile failed",
                    "status": "SG",
                    "code": None,
                    "wall_time": 5,
                },
            },
        )


class FakeCodeAnalysisService:
    @staticmethod
    async def analyze(*, code: str) -> CodeAnalysisResultDTO:
        _ = code

        return CodeAnalysisResultDTO.model_validate(
            {
                "diagnostics": [
                    {
                        "line": 1,
                        "column": 10,
                        "stop_line": 1,
                        "stop_column": 13,
                        "severity": "error",
                        "message": "`str` is not assignable to `int`",
                        "name": "bad-assignment",
                    },
                ],
            },
        )


async def test_execution_run_success(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="1",
        slug="lesson-1",
        name="Lesson 1",
        body_markdown="body",
        code_editor_default="",
        cases=CASES,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonService

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "class User: pass"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert len(data["cases"]) == 2

    app.dependency_overrides.pop(get_piston_service, None)


async def test_execution_analyze_success(client: httpx.AsyncClient) -> None:
    app.dependency_overrides[get_code_analysis_service] = FakeCodeAnalysisService

    response = await client.post(
        "/api/v1/execute/analyze",
        json={"code": 'age: int = "18"'},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["diagnostics"]) == 1
    assert data["diagnostics"][0]["severity"] == "error"

    app.dependency_overrides.pop(get_code_analysis_service, None)


async def test_execution_invalid_output_returns_runtime_error(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="3",
        slug="lesson-3",
        name="Lesson 3",
        body_markdown="body",
        code_editor_default="",
        cases=CASES,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonServiceInvalidOutput

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "class User: pass"},
    )

    assert response.status_code == 503

    app.dependency_overrides.pop(get_piston_service, None)


async def test_execution_no_code_lesson_rejects_run(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="4",
        no_code=True,
        slug="lesson-4",
        name="Lesson 4",
        body_markdown="body",
        code_editor_default="",
        cases=[],
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "print('hello')"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "runtime_error"
    assert data["stderr"] == "This lesson does not have a coding task."


async def test_execution_rate_limit(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="2",
        slug="lesson-2",
        name="Lesson 2",
        body_markdown="body",
        code_editor_default="",
        cases=CASES,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonService
    limiter = ExecutionRateLimiter(max_requests=1, window_sec=3600)
    app.dependency_overrides[get_execution_rate_limiter] = lambda: limiter

    payload = {"lesson_id": str(lesson.id), "code": "class User: pass"}
    first = await client.post("/api/v1/execute/run", json=payload)
    second = await client.post("/api/v1/execute/run", json=payload)

    assert first.status_code == 200
    assert second.status_code == 429

    app.dependency_overrides.pop(get_piston_service, None)
    app.dependency_overrides.pop(get_execution_rate_limiter, None)


async def test_execution_wrong_answer(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="4",
        slug="lesson-4",
        name="Lesson 4",
        body_markdown="body",
        code_editor_default="",
        cases=CASES,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonServiceWrongAnswer

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "class User: pass"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "wrong_answer"
    assert len(data["cases"]) == 2
    assert data["cases"][0]["ok"] is False

    app.dependency_overrides.pop(get_piston_service, None)


async def test_execution_runtime_error_includes_stderr(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="5",
        slug="lesson-5",
        name="Lesson 5",
        body_markdown="body",
        code_editor_default="",
        cases=[CASES[0]],
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonServiceRuntimeError

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "class User: pass"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "runtime_error"
    assert data["stderr"] == "boom"

    app.dependency_overrides.pop(get_piston_service, None)


async def test_execution_compile_error(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="6",
        slug="lesson-6",
        name="Lesson 6",
        body_markdown="body",
        code_editor_default="",
        cases=[CASES[0]],
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonServiceCompileError

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "class User: pass"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compile_error"
    assert data["stderr"] == "compile failed"

    app.dependency_overrides.pop(get_piston_service, None)


async def test_execution_runtime_error_without_stderr_is_invalid_output(
        client: httpx.AsyncClient,
        db_session: AsyncSession,
) -> None:
    lesson = Lesson(
        order="7",
        slug="lesson-7",
        name="Lesson 7",
        body_markdown="body",
        code_editor_default="",
        cases=[CASES[0]],
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)

    app.dependency_overrides[get_piston_service] = FakePistonServiceRuntimeErrorEmptyStderr

    response = await client.post(
        "/api/v1/execute/run",
        json={"lesson_id": str(lesson.id), "code": "class User: pass"},
    )

    assert response.status_code == 503

    app.dependency_overrides.pop(get_piston_service, None)
