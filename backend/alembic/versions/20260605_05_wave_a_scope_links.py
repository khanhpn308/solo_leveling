"""add wave A scope and typed link columns

Revision ID: 20260605_05
Revises: 20260605_04
Create Date: 2026-06-05 20:55:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260605_05"
down_revision = "20260605_04"
branch_labels = None
depends_on = None


def has_column(inspector, table_name: str, column_name: str) -> bool:
    return column_name in {item["name"] for item in inspector.get_columns(table_name)}


def ensure_column(table_name: str, column: sa.Column) -> None:
    inspector = sa.inspect(op.get_bind())
    if not has_column(inspector, table_name, column.name):
        op.add_column(table_name, column)


def ensure_index(table_name: str, index_name: str, columns: list[str]) -> None:
    inspector = sa.inspect(op.get_bind())
    existing = {item["name"] for item in inspector.get_indexes(table_name)}
    if index_name not in existing:
        op.create_index(index_name, table_name, columns)


def backfill_low_risk_links() -> None:
    op.execute(
        """
        UPDATE quests
        SET daily_slot_code = quest_role
        WHERE daily_slot_code IS NULL
          AND session_type = 'Daily Quest'
          AND quest_role IN ('core', 'support', 'mini')
        """
    )
    op.execute(
        """
        UPDATE quests
        SET error_log_id = tracker_entry_id
        WHERE error_log_id IS NULL
          AND tracker_type = 'error_log'
          AND tracker_entry_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE quests
        SET writing_entry_id = tracker_entry_id
        WHERE writing_entry_id IS NULL
          AND tracker_type = 'writing_entry'
          AND tracker_entry_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE quests
        SET speaking_entry_id = tracker_entry_id
        WHERE speaking_entry_id IS NULL
          AND tracker_type = 'speaking_entry'
          AND tracker_entry_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE quests
        SET mock_test_id = tracker_entry_id
        WHERE mock_test_id IS NULL
          AND tracker_type = 'mock_test'
          AND tracker_entry_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions
        SET source_test_record_id = source_ref_id
        WHERE source_test_record_id IS NULL
          AND source_type = 'test_record'
          AND source_ref_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions
        SET source_mock_test_id = source_ref_id
        WHERE source_mock_test_id IS NULL
          AND source_type = 'mock_test'
          AND source_ref_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE weakness_suggestions
        SET source_error_log_id = source_ref_id
        WHERE source_error_log_id IS NULL
          AND source_type = 'error_log'
          AND source_ref_id IS NOT NULL
        """
    )


def upgrade() -> None:
    ensure_column("checkins", sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True))
    ensure_column("test_records", sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True))
    ensure_column(
        "skill_rank_suggestions",
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
    )
    ensure_column(
        "skill_rank_history",
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
    )
    ensure_column(
        "weakness_suggestions",
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True),
    )
    ensure_index("checkins", "ix_checkins_campaign_id", ["campaign_id"])
    ensure_index("test_records", "ix_test_records_campaign_id", ["campaign_id"])
    ensure_index("skill_rank_suggestions", "ix_skill_rank_suggestions_campaign_id", ["campaign_id"])
    ensure_index("skill_rank_history", "ix_skill_rank_history_campaign_id", ["campaign_id"])
    ensure_index("weakness_suggestions", "ix_weakness_suggestions_campaign_id", ["campaign_id"])

    ensure_column("quests", sa.Column("daily_slot_code", sa.String(length=20), nullable=True))
    ensure_column("quests", sa.Column("error_log_id", sa.Integer(), sa.ForeignKey("error_logs.id"), nullable=True))
    ensure_column("quests", sa.Column("writing_entry_id", sa.Integer(), sa.ForeignKey("writing_entries.id"), nullable=True))
    ensure_column("quests", sa.Column("speaking_entry_id", sa.Integer(), sa.ForeignKey("speaking_entries.id"), nullable=True))
    ensure_column("quests", sa.Column("mock_test_id", sa.Integer(), sa.ForeignKey("mock_tests.id"), nullable=True))
    ensure_index("quests", "ix_quests_daily_slot_code", ["daily_slot_code"])
    ensure_index("quests", "ix_quests_error_log_id", ["error_log_id"])
    ensure_index("quests", "ix_quests_writing_entry_id", ["writing_entry_id"])
    ensure_index("quests", "ix_quests_speaking_entry_id", ["speaking_entry_id"])
    ensure_index("quests", "ix_quests_mock_test_id", ["mock_test_id"])

    ensure_column(
        "weakness_suggestions",
        sa.Column("source_test_record_id", sa.Integer(), sa.ForeignKey("test_records.id"), nullable=True),
    )
    ensure_column(
        "weakness_suggestions",
        sa.Column("source_mock_test_id", sa.Integer(), sa.ForeignKey("mock_tests.id"), nullable=True),
    )
    ensure_column(
        "weakness_suggestions",
        sa.Column("source_error_log_id", sa.Integer(), sa.ForeignKey("error_logs.id"), nullable=True),
    )
    ensure_column(
        "weakness_suggestions",
        sa.Column("source_quest_id", sa.Integer(), sa.ForeignKey("quests.id"), nullable=True),
    )
    ensure_index("weakness_suggestions", "ix_weakness_suggestions_source_test_record_id", ["source_test_record_id"])
    ensure_index("weakness_suggestions", "ix_weakness_suggestions_source_mock_test_id", ["source_mock_test_id"])
    ensure_index("weakness_suggestions", "ix_weakness_suggestions_source_error_log_id", ["source_error_log_id"])
    ensure_index("weakness_suggestions", "ix_weakness_suggestions_source_quest_id", ["source_quest_id"])

    backfill_low_risk_links()


def downgrade() -> None:
    pass
