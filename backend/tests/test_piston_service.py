import pytest

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput, ExecutionServiceUnavailable
from src.app.domain.services.piston_service import PistonService


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
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


async def test_piston_service_execute_success(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(status_code=200, payload={"run": {"stdout": "{}"}})
    monkeypatch.setattr("src.app.domain.services.piston_service.httpx.AsyncClient", lambda **_: FakeClient(response))

    service = PistonService()
    result = await service.execute(source_code="print('ok')")

    assert result["run"]["stdout"] == "{}"


async def test_piston_service_execute_invalid_output(monkeypatch: pytest.MonkeyPatch) -> None:
    response = FakeResponse(status_code=200, payload=None)
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
