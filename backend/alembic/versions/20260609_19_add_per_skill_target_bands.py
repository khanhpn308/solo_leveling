"""add per-skill target band columns to players

Revision ID: 20260609_19
Revises: 20260609_18
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa

revision = "20260609_19"
down_revision = "20260609_18"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("players", sa.Column("target_listening_band", sa.String(20), nullable=True))
    op.add_column("players", sa.Column("target_reading_band", sa.String(20), nullable=True))
    op.add_column("players", sa.Column("target_writing_band", sa.String(20), nullable=True))
    op.add_column("players", sa.Column("target_speaking_band", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("players", "target_speaking_band")
    op.drop_column("players", "target_writing_band")
    op.drop_column("players", "target_reading_band")
    op.drop_column("players", "target_listening_band")
