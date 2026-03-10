"""add cascade delete to lesson_progress

Revision ID: 0b7e7f6f2a4d
Revises: 642e01a7aceb
Create Date: 2026-03-10 21:35:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b7e7f6f2a4d"
down_revision: Union[str, Sequence[str], None] = "642e01a7aceb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _find_lesson_progress_lesson_fk_name() -> str:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for foreign_key in inspector.get_foreign_keys("lesson_progress"):
        constrained_columns = foreign_key.get("constrained_columns") or []
        referred_table = foreign_key.get("referred_table")

        if constrained_columns == ["lesson_id"] and referred_table == "lessons":
            name = foreign_key.get("name")
            if not name:
                raise RuntimeError("lesson_progress.lesson_id foreign key exists without a name")
            return name

    raise RuntimeError("Could not find lesson_progress.lesson_id foreign key")


def upgrade() -> None:
    """Upgrade schema."""
    foreign_key_name = _find_lesson_progress_lesson_fk_name()

    op.drop_constraint(foreign_key_name, "lesson_progress", type_="foreignkey")
    op.create_foreign_key(
        "fk_lesson_progress_lesson_id_lessons",
        "lesson_progress",
        "lessons",
        ["lesson_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_lesson_progress_lesson_id_lessons",
        "lesson_progress",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_lesson_progress_lesson_id_lessons",
        "lesson_progress",
        "lessons",
        ["lesson_id"],
        ["id"],
    )
