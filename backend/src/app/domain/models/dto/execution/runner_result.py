from pydantic import field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class RunnerStepResultDTO(ExtendedBaseModel):
    status: str | None = None
    code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    wall_time: int | None = None

    @field_validator("wall_time")
    @classmethod
    def validate_wall_time(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            message = "wall_time must be non-negative."
            raise ValueError(message)

        return value


class RunnerExecutionResultDTO(ExtendedBaseModel):
    compile: RunnerStepResultDTO | None = None
    run: RunnerStepResultDTO | None = None
