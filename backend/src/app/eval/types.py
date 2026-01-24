from dataclasses import dataclass

USER_CODE_PLACEHOLDER = "{{USER_CODE}}"


@dataclass(frozen=True)
class EvalCase:
    name: str
    label: str
    is_sample: bool


@dataclass(frozen=True)
class EvalDefinition:
    key: str
    script: str
    cases: list[EvalCase]
