from src.app.domain.services.code_analysis_service import CodeAnalysisService

CODE_ANALYSIS_SERVICE = CodeAnalysisService()


def get_code_analysis_service() -> CodeAnalysisService:
    return CODE_ANALYSIS_SERVICE
