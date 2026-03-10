"""add no_code flag to lessons

Revision ID: 8c7e3c1b5e21
Revises: 0b7e7f6f2a4d
Create Date: 2026-03-10 22:35:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8c7e3c1b5e21"
down_revision: Union[str, Sequence[str], None] = "0b7e7f6f2a4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "lessons",
        sa.Column(
            "no_code",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("lessons", "no_code")
