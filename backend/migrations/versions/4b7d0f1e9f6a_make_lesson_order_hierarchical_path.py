"""make lesson order hierarchical path

Revision ID: 4b7d0f1e9f6a
Revises: e558abd4298f
Create Date: 2026-03-10 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4b7d0f1e9f6a"
down_revision: Union[str, Sequence[str], None] = "e558abd4298f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "lessons",
        "order",
        existing_type=sa.Integer(),
        type_=sa.String(length=64),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "lessons",
        "order",
        existing_type=sa.String(length=64),
        type_=sa.Integer(),
        existing_nullable=False,
    )
