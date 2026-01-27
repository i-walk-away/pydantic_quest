"""lesson progress

Revision ID: 1f2e3d4c5b6a
Revises: 7a9b4c7f9140
Create Date: 2026-01-27 02:05:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1f2e3d4c5b6a'
down_revision: Union[str, Sequence[str], None] = '7a9b4c7f9140'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'lesson_progress',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('lesson_id', sa.Uuid(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], name='fk_lesson_progress_lesson_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_lesson_progress_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'lesson_id', name='uq_lesson_progress_user_lesson'),
    )
    op.create_index('ix_lesson_progress_lesson_id', 'lesson_progress', ['lesson_id'], unique=False)
    op.create_index('ix_lesson_progress_user_id', 'lesson_progress', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_lesson_progress_user_id', table_name='lesson_progress')
    op.drop_index('ix_lesson_progress_lesson_id', table_name='lesson_progress')
    op.drop_table('lesson_progress')
