"""add questions to lessons

Revision ID: 3fcb1df8a9f2
Revises: 8c7e3c1b5e21
Create Date: 2026-03-18 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "3fcb1df8a9f2"
down_revision = "8c7e3c1b5e21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("lessons")}

    if "questions" not in existing_columns:
        op.add_column(
            "lessons",
            sa.Column("questions", sa.JSON(), nullable=True),
        )

    op.execute(sa.text("UPDATE lessons SET questions = '[]' WHERE questions IS NULL"))
    op.alter_column("lessons", "questions", existing_type=sa.JSON(), nullable=False)


def downgrade() -> None:
    op.drop_column("lessons", "questions")
