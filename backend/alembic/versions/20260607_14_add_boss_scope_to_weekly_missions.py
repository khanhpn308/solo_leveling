"""add boss_scope to weekly_missions

Revision ID: 20260607_14
Revises: 20260607_13
Create Date: 2026-06-07 12:30:00

Adds the missing boss_scope column to weekly_missions that was referenced
in the WeeklyMission model but not covered by any prior migration.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260607_14"
down_revision = "20260607_13"
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

    if has_table(inspector, "weekly_missions"):
        if not has_column(inspector, "weekly_missions", "boss_scope"):
            op.add_column(
                "weekly_missions",
                sa.Column("boss_scope", sa.String(length=50), nullable=False, server_default="player"),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if has_table(inspector, "weekly_missions"):
        try:
            op.drop_column("weekly_missions", "boss_scope")
        except Exception:
            pass
