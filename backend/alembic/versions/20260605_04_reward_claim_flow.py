"""add reward claim fields for quests and weekly missions

Revision ID: 20260605_04
Revises: 20260603_03
Create Date: 2026-06-05 10:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260605_04"
down_revision = "20260603_03"
branch_labels = None
depends_on = None


def ensure_column(table_name: str, column: sa.Column) -> None:
    inspector = sa.inspect(op.get_bind())
    existing = {item["name"] for item in inspector.get_columns(table_name)}
    if column.name not in existing:
        op.add_column(table_name, column)


def ensure_index(table_name: str, index_name: str, columns: list[str]) -> None:
    inspector = sa.inspect(op.get_bind())
    existing = {item["name"] for item in inspector.get_indexes(table_name)}
    if index_name not in existing:
        op.create_index(index_name, table_name, columns)


def upgrade() -> None:
    ensure_column("quests", sa.Column("reward_claimed", sa.Boolean(), nullable=False, server_default=sa.false()))
    ensure_column("quests", sa.Column("reward_claimed_at", sa.DateTime(), nullable=True))
    ensure_index("quests", "ix_quests_reward_claimed", ["reward_claimed"])

    ensure_column("weekly_missions", sa.Column("reward_claimed", sa.Boolean(), nullable=False, server_default=sa.false()))
    ensure_column("weekly_missions", sa.Column("reward_claimed_at", sa.DateTime(), nullable=True))
    ensure_index("weekly_missions", "ix_weekly_missions_reward_claimed", ["reward_claimed"])

    op.execute(
        """
        UPDATE quests
        SET reward_claimed = 1,
            reward_claimed_at = COALESCE(reward_claimed_at, completed_at, NOW())
        WHERE completed = 1
        """
    )
    op.execute(
        """
        UPDATE weekly_missions
        SET reward_claimed = 1,
            reward_claimed_at = COALESCE(reward_claimed_at, completed_at, NOW())
        WHERE status = 'completed'
        """
    )


def downgrade() -> None:
    pass
