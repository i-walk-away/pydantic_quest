"""github oauth fields

Revision ID: 9b1d8c5e4d7a
Revises: 80212e13c5f9
Create Date: 2026-01-21 12:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9b1d8c5e4d7a"
down_revision: Union[str, Sequence[str], None] = "80212e13c5f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("github_id", sa.BigInteger(), nullable=True))
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=True
    )
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_github_id", "users", ["github_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_users_github_id", "users", type_="unique")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=False
    )
    op.drop_column("users", "github_id")
    op.drop_column("users", "email")
