from typing import ClassVar, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

TDTO = TypeVar("TDTO", bound=BaseModel)


class Base(DeclarativeBase):
    # when inheriting from base,
    # populate this field with a corresponding DTO class.
    dto_class: ClassVar[Type[TDTO] | None] = None

    def to_dto(self) -> TDTO:
        """
        Converts a database model into a BaseModel DTO object.
        """
        if self.dto_class is None:
            raise ValueError(f"{type(self).__name__}.dto_class is not set")

        return self.dto_class.model_validate(obj=self, from_attributes=True)
