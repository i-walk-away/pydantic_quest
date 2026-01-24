from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class ExecutionCaseDTO(ExtendedBaseModel):
    name: str
    label: str
    ok: bool
    reason: str | None = None
