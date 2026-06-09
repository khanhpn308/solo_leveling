"""add quest tracking fields and xp transaction tables

Revision ID: 20260607_11
Revises: 20260607_10
Create Date: 2026-06-07 01:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260607_11"
down_revision = "20260607_10"
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

    # Add columns to quest_templates
    if has_table(inspector, "quest_templates"):
        if not has_column(inspector, "quest_templates", "quest_track_code"):
            op.add_column("quest_templates", sa.Column("quest_track_code", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "quest_templates", "activity_type"):
            op.add_column("quest_templates", sa.Column("activity_type", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "quest_templates", "reward_skill_id"):
            op.add_column("quest_templates", sa.Column("reward_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=True))
        if not has_column(inspector, "quest_templates", "target_metric"):
            op.add_column("quest_templates", sa.Column("target_metric", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "quest_templates", "target_count"):
            op.add_column("quest_templates", sa.Column("target_count", sa.Integer(), nullable=False, server_default="1"))
        if not has_column(inspector, "quest_templates", "completion_payload"):
            op.add_column("quest_templates", sa.Column("completion_payload", sa.Text(), nullable=True))

    # Add columns to quests
    if has_table(inspector, "quests"):
        if not has_column(inspector, "quests", "quest_track_code"):
            op.add_column("quests", sa.Column("quest_track_code", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "quests", "activity_type"):
            op.add_column("quests", sa.Column("activity_type", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "quests", "reward_skill_id"):
            op.add_column("quests", sa.Column("reward_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=True))
        if not has_column(inspector, "quests", "target_metric"):
            op.add_column("quests", sa.Column("target_metric", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "quests", "target_count"):
            op.add_column("quests", sa.Column("target_count", sa.Integer(), nullable=False, server_default="1"))
        if not has_column(inspector, "quests", "completion_payload"):
            op.add_column("quests", sa.Column("completion_payload", sa.Text(), nullable=True))

    # Add columns to weekly_missions
    if has_table(inspector, "weekly_missions"):
        if not has_column(inspector, "weekly_missions", "primary_skill_id"):
            op.add_column("weekly_missions", sa.Column("primary_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=True))
        if not has_column(inspector, "weekly_missions", "mission_track_code"):
            op.add_column("weekly_missions", sa.Column("mission_track_code", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "weekly_missions", "activity_type"):
            op.add_column("weekly_missions", sa.Column("activity_type", sa.String(length=80), nullable=False, server_default=""))
        if not has_column(inspector, "weekly_missions", "reward_skill_id"):
            op.add_column("weekly_missions", sa.Column("reward_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=True))
        if not has_column(inspector, "weekly_missions", "boss_scope"):
            op.add_column("weekly_missions", sa.Column("boss_scope", sa.String(length=50), nullable=False, server_default="player"))

    # Create skill_xp_transactions table
    if not has_table(inspector, "skill_xp_transactions"):
        op.create_table(
            "skill_xp_transactions",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("transaction_type", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("idempotency_key", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_skill_xp_transactions_campaign_id", "skill_xp_transactions", ["campaign_id"])
        op.create_index("ix_skill_xp_transactions_skill_id", "skill_xp_transactions", ["skill_id"])
        op.create_unique_constraint("uq_skill_xp_transactions_idempotency", "skill_xp_transactions", ["idempotency_key"])

    # Create player_xp_transactions table
    if not has_table(inspector, "player_xp_transactions"):
        op.create_table(
            "player_xp_transactions",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("transaction_type", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("idempotency_key", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_player_xp_transactions_campaign_id", "player_xp_transactions", ["campaign_id"])
        op.create_index("ix_player_xp_transactions_player_id", "player_xp_transactions", ["player_id"])
        op.create_unique_constraint("uq_player_xp_transactions_idempotency", "player_xp_transactions", ["idempotency_key"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Drop tables if exist
    if has_table(inspector, "player_xp_transactions"):
        op.drop_table("player_xp_transactions")
    if has_table(inspector, "skill_xp_transactions"):
        op.drop_table("skill_xp_transactions")

    # Drop added columns from weekly_missions
    if has_table(inspector, "weekly_missions"):
        try:
            op.drop_column("weekly_missions", "reward_skill_id")
        except Exception:
            pass
        try:
            op.drop_column("weekly_missions", "activity_type")
        except Exception:
            pass
        try:
            op.drop_column("weekly_missions", "mission_track_code")
        except Exception:
            pass
        try:
            op.drop_column("weekly_missions", "primary_skill_id")
        except Exception:
            pass

    # Drop added columns from quests
    if has_table(inspector, "quests"):
        for col in ("completion_payload", "target_count", "target_metric", "reward_skill_id", "activity_type", "quest_track_code"):
            try:
                op.drop_column("quests", col)
            except Exception:
                pass

    # Drop added columns from quest_templates
    if has_table(inspector, "quest_templates"):
        for col in ("completion_payload", "target_count", "target_metric", "reward_skill_id", "activity_type", "quest_track_code"):
            try:
                op.drop_column("quest_templates", col)
            except Exception:
                pass
