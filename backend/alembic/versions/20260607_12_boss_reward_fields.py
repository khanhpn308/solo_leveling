"""add boss reward fields

Revision ID: 20260607_12
Revises: 20260607_11
Create Date: 2026-06-07 02:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260607_12"
down_revision = "20260607_11"
branch_labels = None
depends_on = None


def has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def has_column(inspector, table_name: str, column_name: str) -> bool:
    cols = [c.get("name") for c in inspector.get_columns(table_name)]
    return column_name in cols


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if has_table(inspector, "boss_battles"):
        if not has_column(inspector, "boss_battles", "boss_scope"):
            op.add_column("boss_battles", sa.Column("boss_scope", sa.String(length=50), nullable=False, server_default="player"))
        if not has_column(inspector, "boss_battles", "reward_skill_id"):
            op.add_column("boss_battles", sa.Column("reward_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=True))
        if not has_column(inspector, "boss_battles", "reward_claimed"):
            op.add_column("boss_battles", sa.Column("reward_claimed", sa.Boolean(), nullable=False, server_default=sa.text("0")))
        if not has_column(inspector, "boss_battles", "reward_claimed_at"):
            op.add_column("boss_battles", sa.Column("reward_claimed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if has_table(inspector, "boss_battles"):
        try:
            op.drop_column("boss_battles", "reward_claimed_at")
        except Exception:
            pass
        try:
            op.drop_column("boss_battles", "reward_claimed")
        except Exception:
            pass
        try:
            op.drop_column("boss_battles", "reward_skill_id")
        except Exception:
            pass
        try:
            op.drop_column("boss_battles", "boss_scope")
        except Exception:
            pass
