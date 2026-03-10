import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from src.app.core.exceptions.execution_exc import ExecutionServiceUnavailable
from src.app.domain.models.dto.execution.code_analysis_diagnostic import (
    CodeAnalysisDiagnosticDTO,
)
from src.app.domain.models.dto.execution.code_analysis_result import CodeAnalysisResultDTO


class CodeAnalysisService:
    def __init__(self, *, timeout_sec: float = 4.0) -> None:
        self.timeout_sec = timeout_sec

    async def analyze(self, *, code: str) -> CodeAnalysisResultDTO:
        with TemporaryDirectory(prefix="pyrefly-") as temp_dir:
            file_path = Path(temp_dir) / "lesson_code.py"
            file_path.write_text(code, encoding="utf-8")

            process = await asyncio.create_subprocess_exec(
                "pyrefly",
                "check",
                "--python-version=3.12",
                "--output-format=json",
                str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    fut=process.communicate(),
                    timeout=self.timeout_sec,
                )
            except TimeoutError as exc:
                process.kill()
                await process.communicate()
                message = "Static analysis timed out."
                raise ExecutionServiceUnavailable(detail=message) from exc

        if process.returncode not in {0, 1}:
            detail = stderr.decode("utf-8").strip() or "Static analysis failed."
            raise ExecutionServiceUnavailable(detail=detail)

        try:
            payload = json.loads(stdout.decode("utf-8"))
        except json.JSONDecodeError as exc:
            message = "Static analysis returned invalid output."
            raise ExecutionServiceUnavailable(detail=message) from exc

        diagnostics = [
            CodeAnalysisDiagnosticDTO(
                line=item["line"],
                column=item["column"],
                stop_line=item["stop_line"],
                stop_column=item["stop_column"],
                severity=item["severity"],
                message=item.get("concise_description") or item.get("description") or "Unknown issue.",
                code=item.get("code"),
                name=item.get("name"),
            )
            for item in payload.get("errors", [])
        ]

        return CodeAnalysisResultDTO(diagnostics=diagnostics)
