from __future__ import annotations

from pydantic import Field, model_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel


class UpdateUserDTO(ExtendedBaseModel):
    username: str | None = None
    email: str | None = None
    current_password: str | None = Field(default=None, exclude=True)
    new_password: str | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validate_password_change_pair(self) -> UpdateUserDTO:
        """
        Validate password change fields as a pair.

        Password update requests must include both the current and the new
        password, so partial payloads are rejected at DTO validation time.

        :return: validated dto
        """
        if self.new_password and not self.current_password:
            message = "Current password is required."
            raise ValueError(message)

        if self.current_password and not self.new_password:
            message = "New password is required."
            raise ValueError(message)

        return self
