from pydantic import ValidationInfo, field_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class LessonCaseDTO(ExtendedBaseModel):
    name: str
    label: str
    script: str
    hidden: bool = False

    @field_validator("name", "label", "script")
    @classmethod
    def validate_non_blank(cls, value: str, info: ValidationInfo) -> str:
        """
        Validate case text fields are not blank.

        :param value: field value
        :param info: validation info

        :return: normalized value
        """
        normalized = value.strip()
        if not normalized:
            field_name = info.field_name or "field"
            message = f"{field_name} must not be empty."
            raise ValueError(message)

        return normalized
