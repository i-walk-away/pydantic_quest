from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    # when inheriting from base,
    # populate this field with a corresponding DTO class.
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
