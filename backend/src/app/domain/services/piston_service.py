import asyncio
import time

import httpx
from pydantic import ValidationError

from src.app.core.exceptions.execution_exc import ExecutionInvalidOutput, ExecutionServiceUnavailable
from src.app.domain.models.dto.execution.runner_result import RunnerExecutionResultDTO, RunnerStepResultDTO
from src.app.domain.services.code_runner import CodeRunner
from src.cfg.cfg import settings


class PistonService(CodeRunner):
    def __init__(self) -> None:
        """
        Initialize Piston service.

        :return: None
        """
        self.base_url = settings.execution.piston_url
        self._last_health_check = 0.0

    async def execute(self, source_code: str) -> RunnerExecutionResultDTO:
        """
        Execute code through the Piston API.

        :param source_code: combined evaluation script and user code

        :return: normalized runner execution result
        """
        await self._ensure_available()
        payload = {
            "language": settings.execution.language,
            "version": settings.execution.version,
            "files": [{"name": "main.py", "content": source_code}],
            "stdin": "",
            "compile_timeout": settings.execution.compile_timeout_ms,
            "run_timeout": settings.execution.run_timeout_ms,
            "compile_memory_limit": settings.execution.compile_memory_limit_bytes,
            "run_memory_limit": settings.execution.run_memory_limit_bytes,
            "output_max_size": settings.execution.output_max_size,
            "max_file_size": settings.execution.max_file_size,
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
                        raw_payload = response.json()

                        return self._to_runner_result(payload=raw_payload)
                    except (ValueError, ValidationError) as exc:
                        raise ExecutionInvalidOutput from exc

                last_error = ExecutionServiceUnavailable()
            except httpx.RequestError as exc:
                last_error = exc

            if attempt < retries:
                await asyncio.sleep(delay=settings.execution.retry_delay_ms / 1000)

        raise ExecutionServiceUnavailable from last_error

    async def _ensure_available(self) -> None:
        """
        Ensure Piston API is reachable.

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

    def _to_runner_result(self, payload: dict) -> RunnerExecutionResultDTO:
        """
        Convert Piston response payload to runner result DTO.

        :param payload: Piston response payload

        :return: normalized runner result
        """
        compile_payload = payload.get("compile")

        if isinstance(compile_payload, dict):
            compile_code = compile_payload.get("code")
            compile_signal = compile_payload.get("signal")

            if (isinstance(compile_code, int) and compile_code != 0) or compile_signal is not None:
                compile_step = RunnerStepResultDTO.model_validate(
                    obj={
                        "status": "SG",
                        "code": 1,
                        "stdout": compile_payload.get("stdout"),
                        "stderr": self._resolve_step_stderr(step=compile_payload),
                        "wall_time": self._parse_duration_ms(value=compile_payload.get("time")),
                    },
                )

                return RunnerExecutionResultDTO.model_validate(
                    obj={
                        "compile": compile_step.model_dump(),
                    },
                )

        run_payload = payload.get("run")

        if not isinstance(run_payload, dict):
            raise ExecutionInvalidOutput

        run_code = run_payload.get("code")
        run_signal = run_payload.get("signal")
        run_status: str | None = None

        if run_signal == "SIGKILL":
            run_status = "TO"
            run_code = 1
        elif (isinstance(run_code, int) and run_code != 0) or run_signal is not None:
            run_status = "RE"
            run_code = 1
        elif run_code is None:
            run_code = 0

        run_step = RunnerStepResultDTO.model_validate(
            obj={
                "status": run_status,
                "code": run_code,
                "stdout": run_payload.get("stdout"),
                "stderr": self._resolve_step_stderr(step=run_payload),
                "wall_time": self._parse_duration_ms(value=run_payload.get("time")),
            },
        )

        return RunnerExecutionResultDTO.model_validate(
            obj={
                "run": run_step.model_dump(),
            },
        )

    @staticmethod
    def _parse_duration_ms(value: object) -> int | None:
        """
        Parse Piston time value into milliseconds.

        :param value: raw Piston time field value

        :return: duration in milliseconds
        """
        if value is None:
            return None

        try:
            seconds = float(value)
        except (TypeError, ValueError):
            return None

        if seconds < 0:
            raise ExecutionInvalidOutput

        return int(seconds * 1000)

    @staticmethod
    def _resolve_step_stderr(step: dict) -> str | None:
        """
        Resolve stderr-like text from Piston step payload.

        :param step: Piston compile or run payload

        :return: normalized stderr text
        """
        stderr = step.get("stderr")
        message = step.get("message")

        if isinstance(stderr, str) and stderr:
            return stderr

        if isinstance(message, str) and message:
            return message

        return None
