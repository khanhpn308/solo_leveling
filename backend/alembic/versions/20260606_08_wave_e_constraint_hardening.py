"""wave E constraint hardening

Revision ID: 20260606_08
Revises: 20260605_07
Create Date: 2026-06-06 00:40:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260606_08"
down_revision = "20260605_07"
branch_labels = None
depends_on = None


def scalar_int(sql: str) -> int:
    bind = op.get_bind()
    return int(bind.execute(sa.text(sql)).scalar() or 0)


def assert_zero(sql: str, label: str) -> None:
    count = scalar_int(sql)
    if count != 0:
        raise RuntimeError(f"Wave E preflight failed: {label} has {count} violating rows")


def sync_daily_slot_code() -> None:
    op.execute(
        """
        UPDATE quests
        SET daily_slot_code = quest_role
        WHERE daily_slot_code IS NULL
          AND session_type = 'Daily Quest'
          AND quest_role IN ('core', 'support', 'mini')
        """
    )


def run_preflight_checks() -> None:
    checks = [
        ("SELECT COUNT(*) FROM checkins WHERE campaign_id IS NULL", "checkins.campaign_id IS NULL"),
        ("SELECT COUNT(*) FROM test_records WHERE campaign_id IS NULL", "test_records.campaign_id IS NULL"),
        (
            "SELECT COUNT(*) FROM skill_rank_suggestions WHERE campaign_id IS NULL",
            "skill_rank_suggestions.campaign_id IS NULL",
        ),
        (
            "SELECT COUNT(*) FROM skill_rank_history WHERE campaign_id IS NULL",
            "skill_rank_history.campaign_id IS NULL",
        ),
        (
            "SELECT COUNT(*) FROM weakness_suggestions WHERE campaign_id IS NULL",
            "weakness_suggestions.campaign_id IS NULL",
        ),
        ("SELECT COUNT(*) FROM quests WHERE campaign_id IS NULL", "quests.campaign_id IS NULL"),
        (
            """
            SELECT COUNT(*)
            FROM quests
            WHERE session_type = 'Daily Quest'
              AND quest_role IN ('core', 'support', 'mini')
              AND daily_slot_code IS NULL
            """,
            "daily quests with NULL daily_slot_code",
        ),
        (
            """
            SELECT COUNT(*)
            FROM (
                SELECT campaign_id, checkin_date
                FROM checkins
                GROUP BY campaign_id, checkin_date
                HAVING COUNT(*) > 1
            ) duplicate_checkins
            """,
            "duplicate (campaign_id, checkin_date) rows",
        ),
        (
            """
            SELECT COUNT(*)
            FROM (
                SELECT campaign_id, quest_date, daily_slot_code
                FROM quests
                WHERE session_type = 'Daily Quest'
                  AND quest_role IN ('core', 'support', 'mini')
                GROUP BY campaign_id, quest_date, daily_slot_code
                HAVING COUNT(*) > 1
            ) duplicate_daily_slots
            """,
            "duplicate (campaign_id, quest_date, daily_slot_code) daily quests",
        ),
    ]
    for sql, label in checks:
        assert_zero(sql, label)


def upgrade() -> None:
    sync_daily_slot_code()
    run_preflight_checks()

    op.alter_column("checkins", "campaign_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("test_records", "campaign_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("skill_rank_suggestions", "campaign_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("skill_rank_history", "campaign_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("weakness_suggestions", "campaign_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("quests", "campaign_id", existing_type=sa.Integer(), nullable=False)

    op.drop_constraint("uq_checkin_date", "checkins", type_="unique")
    op.create_unique_constraint("uq_checkins_campaign_date", "checkins", ["campaign_id", "checkin_date"])
    op.create_unique_constraint(
        "uq_quests_campaign_date_daily_slot",
        "quests",
        ["campaign_id", "quest_date", "daily_slot_code"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_quests_campaign_date_daily_slot", "quests", type_="unique")
    op.drop_constraint("uq_checkins_campaign_date", "checkins", type_="unique")
    op.create_unique_constraint("uq_checkin_date", "checkins", ["checkin_date"])

    op.alter_column("quests", "campaign_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("weakness_suggestions", "campaign_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("skill_rank_history", "campaign_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("skill_rank_suggestions", "campaign_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("test_records", "campaign_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("checkins", "campaign_id", existing_type=sa.Integer(), nullable=True)
