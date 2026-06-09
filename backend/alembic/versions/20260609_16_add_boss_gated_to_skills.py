"""add boss_gated to skills

Revision ID: 20260609_16
Revises: 20260609_15
Create Date: 2026-06-09 12:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260609_16"
down_revision = "20260609_15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("boss_gated", sa.Boolean(), server_default="1", nullable=False))


def downgrade() -> None:
    op.drop_column("skills", "boss_gated")
