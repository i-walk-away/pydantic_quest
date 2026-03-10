from __future__ import annotations

import httpx
import pytest

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput, ExecutionServiceUnavailable
from src.app.domain.services.piston_service import PistonService


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | list[dict] | None = None) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict | list[dict]:
        if self._payload is None:
            message = "invalid json"
            raise ValueError(message)

        return self._payload


class FakeClient:
    def __init__(self, response: FakeResponse, get_response: FakeResponse | None = None) -> None:
        self.response = response
        self.get_response = get_response or FakeResponse(status_code=200, payload=[{"language": "python"}])

    async def post(self, *, url: str, json: dict) -> FakeResponse:
        _ = (url, json)

        return self.response

    async def get(self, *, url: str) -> FakeResponse:
        _ = url

        return self.get_response

    async def __aenter__(self) -> FakeClient:
        return self

    async def __aexit__(
            self,
            _exc_type: type[BaseException] | None,
            _exc: BaseException | None,
            _tb: object | None,
    ) -> None:
        return None


class Recorder:
    def __init__(self, *, post_effects: list[FakeResponse | Exception], get_response: FakeResponse) -> None:
        self.post_effects = post_effects
        self.get_response = get_response
        self.post_calls = 0
        self.get_calls = 0


class RecorderClient:
    def __init__(self, recorder: Recorder) -> None:
        self.recorder = recorder

    async def post(self, *, url: str, json: dict) -> FakeResponse:
        _ = (url, json)
        self.recorder.post_calls += 1
        effect = self.recorder.post_effects.pop(0)

        if isinstance(effect, Exception):
            raise effect

        return effect

    async def get(self, *, url: str) -> FakeResponse:
        _ = url
        self.recorder.get_calls += 1

        return self.recorder.get_response

    async def __aenter__(self) -> RecorderClient:
        return self

    async def __aexit__(
            self,
            _exc_type: type[BaseException] | None,
            _exc: BaseException | None,
            _tb: object | None,
    ) -> None:
        return None


async def test_piston_service_execute_success(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(
        status_code=200,
        payload={"run": {"stdout": "{}", "stderr": "", "code": 0, "signal": None, "time": 0.1}},
    )
    monkeypatch.setattr("src.app.domain.services.piston_service.httpx.AsyncClient", lambda **_: FakeClient(response))

    service = PistonService()
    result = await service.execute(source_code="print('ok')")

    assert result.run is not None
    assert result.run.stdout == "{}"


async def test_piston_service_execute_invalid_output(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(status_code=200, payload={"stdout": "{}"})
    monkeypatch.setattr("src.app.domain.services.piston_service.httpx.AsyncClient", lambda **_: FakeClient(response))

    service = PistonService()
    with pytest.raises(ExecutionInvalidOutput):
        await service.execute(source_code="print('ok')")


async def test_piston_service_execute_service_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(status_code=503, payload={"error": "down"})
    monkeypatch.setattr("src.app.domain.services.piston_service.httpx.AsyncClient", lambda **_: FakeClient(response))

    service = PistonService()
    with pytest.raises(ExecutionServiceUnavailable):
        await service.execute(source_code="print('ok')")


async def test_piston_service_compile_error(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(
        status_code=200,
        payload={
            "compile": {
                "stdout": "",
                "stderr": "compile failed",
                "code": 1,
                "signal": None,
                "time": 0.1,
            },
        },
    )
    monkeypatch.setattr("src.app.domain.services.piston_service.httpx.AsyncClient", lambda **_: FakeClient(response))

    service = PistonService()
    result = await service.execute(source_code="print('ok')")

    assert result.compile is not None
    assert result.compile.status == "SG"


async def test_piston_service_retries_request_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    success_response = FakeResponse(
        status_code=200,
        payload={"run": {"stdout": "{}", "stderr": "", "code": 0, "signal": None, "time": 0.1}},
    )
    recorder = Recorder(
        post_effects=[httpx.RequestError("boom"), success_response],
        get_response=FakeResponse(status_code=200, payload=[{"language": "python"}]),
    )

    async def fake_sleep(delay: float) -> None:
        _ = delay

    monkeypatch.setattr(
        "src.app.domain.services.piston_service.httpx.AsyncClient",
        lambda **_: RecorderClient(recorder=recorder),
    )
    monkeypatch.setattr("src.app.domain.services.piston_service.asyncio.sleep", fake_sleep)

    service = PistonService()
    result = await service.execute(source_code="print('ok')")

    assert result.run is not None
    assert recorder.post_calls == 2


async def test_piston_service_health_check_uses_ttl_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    success_response = FakeResponse(
        status_code=200,
        payload={"run": {"stdout": "{}", "stderr": "", "code": 0, "signal": None, "time": 0.1}},
    )
    recorder = Recorder(
        post_effects=[success_response, success_response],
        get_response=FakeResponse(status_code=200, payload=[{"language": "python"}]),
    )
    time_values = iter([100.0, 101.0])

    monkeypatch.setattr(
        "src.app.domain.services.piston_service.httpx.AsyncClient",
        lambda **_: RecorderClient(recorder=recorder),
    )
    monkeypatch.setattr("src.app.domain.services.piston_service.time.time", lambda: next(time_values))

    service = PistonService()
    await service.execute(source_code="print('one')")
    await service.execute(source_code="print('two')")

    assert recorder.get_calls == 1
    assert recorder.post_calls == 2
