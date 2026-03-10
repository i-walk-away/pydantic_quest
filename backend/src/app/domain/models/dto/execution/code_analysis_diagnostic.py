from typing import Literal

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CodeAnalysisDiagnosticDTO(ExtendedBaseModel):
    line: int
    column: int
    stop_line: int
    stop_column: int
    severity: Literal["error", "warning", "information"]
    message: str
    code: int | None = None
    name: str | None = None
