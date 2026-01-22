"""lesson code editor default

Revision ID: 1d7a4e2f19c3
Revises: 9b1d8c5e4d7a
Create Date: 2026-01-22 02:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1d7a4e2f19c3"
down_revision: Union[str, Sequence[str], None] = "9b1d8c5e4d7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "lessons",
        sa.Column("code_editor_default", sa.Text(), nullable=True)
    )
    op.execute("UPDATE lessons SET code_editor_default = '' WHERE code_editor_default IS NULL")
    op.alter_column(
        "lessons",
        "code_editor_default",
        existing_type=sa.Text(),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("lessons", "code_editor_default")
