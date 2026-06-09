"""add policy tables

Revision ID: 20260609_17
Revises: 20260609_16
Create Date: 2026-06-09 13:15:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260609_17"
down_revision = "20260609_16"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. rank_xp_thresholds
    op.create_table(
        "rank_xp_thresholds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rank_name", sa.String(length=10), nullable=False),
        sa.Column("min_xp", sa.Integer(), nullable=False),
        sa.Column("first_level", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rank_xp_thresholds_id", "rank_xp_thresholds", ["id"], unique=False)
    op.create_index("ix_rank_xp_thresholds_rank_name", "rank_xp_thresholds", ["rank_name"], unique=True)

    # 2. quest_xp_policies
    op.create_table(
        "quest_xp_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("activity_code", sa.String(length=100), nullable=False),
        sa.Column("skill_code", sa.String(length=50), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quest_xp_policies_id", "quest_xp_policies", ["id"], unique=False)
    op.create_index("ix_quest_xp_policies_activity_code", "quest_xp_policies", ["activity_code"], unique=True)

    # 3. weekly_mission_xp_policies
    op.create_table(
        "weekly_mission_xp_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mission_type", sa.String(length=100), nullable=False),
        sa.Column("reward_target_skill", sa.String(length=50), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weekly_mission_xp_policies_id", "weekly_mission_xp_policies", ["id"], unique=False)
    op.create_index("ix_weekly_mission_xp_policies_mission_type", "weekly_mission_xp_policies", ["mission_type"], unique=True)

    # 4. main_quest_xp_policies
    op.create_table(
        "main_quest_xp_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tier_code", sa.String(length=100), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_main_quest_xp_policies_id", "main_quest_xp_policies", ["id"], unique=False)
    op.create_index("ix_main_quest_xp_policies_tier_code", "main_quest_xp_policies", ["tier_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_main_quest_xp_policies_tier_code", table_name="main_quest_xp_policies")
    op.drop_index("ix_main_quest_xp_policies_id", table_name="main_quest_xp_policies")
    op.drop_table("main_quest_xp_policies")

    op.drop_index("ix_weekly_mission_xp_policies_mission_type", table_name="weekly_mission_xp_policies")
    op.drop_index("ix_weekly_mission_xp_policies_id", table_name="weekly_mission_xp_policies")
    op.drop_table("weekly_mission_xp_policies")

    op.drop_index("ix_quest_xp_policies_activity_code", table_name="quest_xp_policies")
    op.drop_index("ix_quest_xp_policies_id", table_name="quest_xp_policies")
    op.drop_table("quest_xp_policies")

    op.drop_index("ix_rank_xp_thresholds_rank_name", table_name="rank_xp_thresholds")
    op.drop_index("ix_rank_xp_thresholds_id", table_name="rank_xp_thresholds")
    op.drop_table("rank_xp_thresholds")
