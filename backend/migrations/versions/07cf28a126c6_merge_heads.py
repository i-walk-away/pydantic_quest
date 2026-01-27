"""merge heads

Revision ID: 07cf28a126c6
Revises: 1f2e3d4c5b6a, 5924f24c7bd7
Create Date: 2026-01-27 00:00:00.000000
"""

from collections.abc import Sequence

revision: str = "07cf28a126c6"
down_revision: tuple[str, str] | None = ("1f2e3d4c5b6a", "5924f24c7bd7")
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """
    Merge heads.
    """


def downgrade() -> None:
    """
    Unmerge heads.
    """
