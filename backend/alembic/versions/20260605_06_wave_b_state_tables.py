"""add wave B campaign skill state and badge unlock tables

Revision ID: 20260605_06
Revises: 20260605_05
Create Date: 2026-06-05 23:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260605_06"
down_revision = "20260605_05"
branch_labels = None
depends_on = None


def has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not has_table("campaign_skill_states"):
        op.create_table(
            "campaign_skill_states",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("rank", sa.String(length=2), nullable=False, server_default="F"),
            sa.Column("confirmed_rank", sa.String(length=2), nullable=False, server_default="F"),
            sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("streak", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("last_practiced", sa.Date(), nullable=True),
            sa.Column("weak_point", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("user_weakness_note", sa.Text(), nullable=False),
            sa.Column("last_system_suggestion_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("campaign_id", "skill_id", name="uq_campaign_skill_states_campaign_skill"),
        )
        op.create_index(
            "ix_campaign_skill_states_campaign_confirmed_rank",
            "campaign_skill_states",
            ["campaign_id", "confirmed_rank"],
        )
        op.create_index("ix_campaign_skill_states_skill_id", "campaign_skill_states", ["skill_id"])

    if not has_table("badge_unlocks"):
        op.create_table(
            "badge_unlocks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("badge_id", sa.Integer(), sa.ForeignKey("badges.id"), nullable=False),
            sa.Column("source_boss_battle_id", sa.Integer(), sa.ForeignKey("boss_battles.id"), nullable=True),
            sa.Column("unlocked_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("campaign_id", "badge_id", name="uq_badge_unlocks_campaign_badge"),
        )
        op.create_index("ix_badge_unlocks_player_id", "badge_unlocks", ["player_id"])
        op.create_index("ix_badge_unlocks_badge_id", "badge_unlocks", ["badge_id"])
        op.create_index("ix_badge_unlocks_source_boss_battle_id", "badge_unlocks", ["source_boss_battle_id"])


def downgrade() -> None:
    if has_table("badge_unlocks"):
        op.drop_index("ix_badge_unlocks_source_boss_battle_id", table_name="badge_unlocks")
        op.drop_index("ix_badge_unlocks_badge_id", table_name="badge_unlocks")
        op.drop_index("ix_badge_unlocks_player_id", table_name="badge_unlocks")
        op.drop_table("badge_unlocks")

    if has_table("campaign_skill_states"):
        op.drop_index("ix_campaign_skill_states_skill_id", table_name="campaign_skill_states")
        op.drop_index("ix_campaign_skill_states_campaign_confirmed_rank", table_name="campaign_skill_states")
        op.drop_table("campaign_skill_states")
