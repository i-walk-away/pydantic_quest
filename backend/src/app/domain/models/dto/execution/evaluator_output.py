from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class EvaluatorCaseOutputDTO(ExtendedBaseModel):
    name: str
    ok: bool
    reason: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            message = "name must not be empty."
            raise ValueError(message)

        return normalized

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:

        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class EvaluatorOutputDTO(ExtendedBaseModel):
    ok: bool
    cases: list[EvaluatorCaseOutputDTO]

    @field_validator("cases")
    @classmethod
    def validate_unique_case_names(
            cls,
            value: list[EvaluatorCaseOutputDTO],
    ) -> list[EvaluatorCaseOutputDTO]:
        names = set()
        for case in value:
            if case.name in names:
                message = f"Duplicate evaluator case name: {case.name}"
                raise ValueError(message)
            names.add(case.name)

        return value
