from src.app.domain.models.dto.execution.code_analysis_diagnostic import (
    CodeAnalysisDiagnosticDTO,
)
from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class CodeAnalysisResultDTO(ExtendedBaseModel):
    diagnostics: list[CodeAnalysisDiagnosticDTO]
