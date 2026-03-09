import asyncio
import time

import httpx
from pydantic import ValidationError

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput, ExecutionServiceUnavailable
from src.app.domain.models.dto.execution.runner_result import RunnerExecutionResultDTO
from src.app.domain.services.code_runner import CodeRunner
from src.cfg.cfg import settings


class PistonService(CodeRunner):
    def __init__(self) -> None:
        """
        Initialize piston service.

        :return: None
        """
        self.base_url = settings.execution.piston_url
        self._last_health_check = 0.0

    async def execute(self, source_code: str) -> RunnerExecutionResultDTO:
        """
        Execute code through the Piston API.

        Health check and retry handling are centralized here so callers receive
        one stable contract for transient runner failures.

        :param source_code: combined evaluation script and user code

        :return: piston response payload
        """
        await self._ensure_available()
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

        retries = max(settings.execution.max_retries, 0)
        last_error: Exception | None = None

        timeout = settings.execution.http_timeout_ms / 1000
        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
                    response = await client.post(
                        url="/api/v2/execute",
                        json=payload,
                    )
                if response.status_code == 200:
                    try:
                        payload = response.json()

                        return RunnerExecutionResultDTO.model_validate(obj=payload)
                    except (ValueError, ValidationError) as exc:
                        raise ExecutionInvalidOutput from exc
                last_error = ExecutionServiceUnavailable()
            except httpx.RequestError as exc:
                last_error = exc

            if attempt < retries:
                await asyncio.sleep(settings.execution.retry_delay_ms / 1000)

        raise ExecutionServiceUnavailable from last_error

    async def _ensure_available(self) -> None:
        """
        Ensure Piston API is reachable.

        The method uses TTL-based caching to avoid making a health-check call
        before every user execution request.

        :return: None
        """
        now = time.time()

        if now - self._last_health_check < settings.execution.health_check_ttl_sec:
            return

        timeout = settings.execution.http_timeout_ms / 1000
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
                response = await client.get(url="/api/v2/runtimes")
        except httpx.RequestError as exc:
            raise ExecutionServiceUnavailable from exc

        if response.status_code != 200:
            raise ExecutionServiceUnavailable

        self._last_health_check = now
