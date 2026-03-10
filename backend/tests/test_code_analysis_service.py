import asyncio

import pytest

from src.app.core.exceptions.execution_exc import ExecutionServiceUnavailable
from src.app.domain.services.code_analysis_service import CodeAnalysisService


async def test_code_analysis_service_reports_type_errors() -> None:
    service = CodeAnalysisService()

    result = await service.analyze(code='age: int = "18"\n')

    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity == "error"
    assert "not assignable" in result.diagnostics[0].message


async def test_code_analysis_service_raises_on_invalid_json(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        returncode = 0

        @staticmethod
        async def communicate() -> tuple[bytes, bytes]:
            return b"not-json", b""

    async def fake_create_subprocess_exec(*args: object, **kwargs: object) -> FakeProcess:
        _ = args
        _ = kwargs

        return FakeProcess()

    monkeypatch.setattr(
        target=asyncio,
        name="create_subprocess_exec",
        value=fake_create_subprocess_exec,
    )

    service = CodeAnalysisService()

    with pytest.raises(ExecutionServiceUnavailable, match="invalid output"):
        await service.analyze(code="x = 1\n")
