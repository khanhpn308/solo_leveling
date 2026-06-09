"""merge deferred_cleanup and boss_reward heads

Revision ID: 20260607_13
Revises: 20260607_12, 75dc49c5ae91
Create Date: 2026-06-07 12:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = "20260607_13"
down_revision = ("20260607_12", "75dc49c5ae91")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge only – no schema changes needed.
    pass


def downgrade() -> None:
    pass
