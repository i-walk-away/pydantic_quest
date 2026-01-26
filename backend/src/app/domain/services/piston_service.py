import httpx

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput, ExecutionServiceUnavailable
from src.cfg.cfg import settings


class PistonService:
    def __init__(self) -> None:
        """
        Initialize piston service.

        :return: None
        """
        self.base_url = settings.execution.piston_url

    async def execute(self, source_code: str) -> dict:
        """
        Execute code through the Piston API.

        :param source_code: combined evaluation script and user code

        :return: piston response payload
        """
        payload = {
            "language": settings.execution.language,
            "version": settings.execution.version,
            "files": [
                {
                    "name": "main.py",
                    "content": source_code,
                },
            ],
            "stdin": "",
            "args": [],
            "run_timeout": settings.execution.run_timeout_ms,
            "compile_timeout": settings.execution.compile_timeout_ms,
            "run_memory_limit": settings.execution.run_memory_limit_bytes,
            "compile_memory_limit": settings.execution.compile_memory_limit_bytes,
        }

        try:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                response = await client.post(
                    url="/api/v2/execute",
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise ExecutionServiceUnavailable from exc

        if response.status_code != 200:
            raise ExecutionServiceUnavailable

        try:
            return response.json()
        except ValueError as exc:
            raise ExecutionInvalidOutput from exc
