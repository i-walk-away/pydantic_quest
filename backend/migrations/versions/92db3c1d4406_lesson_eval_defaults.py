"""lesson eval defaults

Revision ID: 92db3c1d4406
Revises: d387acddcac2
Create Date: 2026-01-24 00:13:18.752244

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '92db3c1d4406'
down_revision: Union[str, Sequence[str], None] = 'd387acddcac2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE lessons SET eval_key = 'lesson_01' WHERE eval_key IS NULL OR eval_key = ''")
    op.alter_column(
        "lessons",
        "eval_key",
        existing_type=sa.String(length=128),
        server_default=sa.text("'lesson_01'"),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "lessons",
        "eval_key",
        existing_type=sa.String(length=128),
        server_default=None,
        existing_nullable=False,
    )
