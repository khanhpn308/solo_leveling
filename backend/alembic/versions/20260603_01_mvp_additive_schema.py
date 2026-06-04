"""Add MVP additive schema for campaign progression and trackers.

Revision ID: 20260603_01
Revises:
Create Date: 2026-06-03 22:20:00
"""

from datetime import date, timedelta

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision = "20260603_01"
down_revision = None
branch_labels = None
depends_on = None


def has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def has_column(inspector, table_name: str, column_name: str) -> bool:
    if not has_table(inspector, table_name):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def ensure_column(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not has_column(inspector, table_name, column.name):
        op.add_column(table_name, column)


def has_index(inspector, table_name: str, index_name: str) -> bool:
    if not has_table(inspector, table_name):
        return False
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def ensure_index(table_name: str, index_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not has_index(inspector, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def create_tables() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not has_table(inspector, "campaigns"):
        op.create_table(
            "campaigns",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_campaigns_player_id", "campaigns", ["player_id"])
        op.create_index("ix_campaigns_start_date", "campaigns", ["start_date"])
        op.create_index("ix_campaigns_end_date", "campaigns", ["end_date"])
        op.create_index("ix_campaigns_status", "campaigns", ["status"])
        op.create_index("ix_campaigns_created_at", "campaigns", ["created_at"])

    if not has_table(inspector, "quest_templates"):
        op.create_table(
            "quest_templates",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("primary_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("base_xp", sa.Integer(), nullable=False, server_default="10"),
            sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="easy"),
            sa.Column("difficulty_description", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("quest_role", sa.String(length=20), nullable=False, server_default="mini"),
            sa.Column("resource_name", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("resource_category", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("resource_note", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("allowed_phase_start", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("allowed_phase_end", sa.Integer(), nullable=False, server_default="5"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.create_index("ix_quest_templates_primary_skill_id", "quest_templates", ["primary_skill_id"])
        op.create_index("ix_quest_templates_difficulty", "quest_templates", ["difficulty"])
        op.create_index("ix_quest_templates_quest_role", "quest_templates", ["quest_role"])
        op.create_index("ix_quest_templates_is_active", "quest_templates", ["is_active"])

    if not has_table(inspector, "weekly_missions"):
        op.create_table(
            "weekly_missions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("week_start", sa.Date(), nullable=False),
            sa.Column("week_end", sa.Date(), nullable=False),
            sa.Column("phase", sa.String(length=80), nullable=False),
            sa.Column("pattern_code", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("reward_xp", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_weekly_missions_campaign_id", "weekly_missions", ["campaign_id"])
        op.create_index("ix_weekly_missions_week_start", "weekly_missions", ["week_start"])
        op.create_index("ix_weekly_missions_week_end", "weekly_missions", ["week_end"])
        op.create_index("ix_weekly_missions_phase", "weekly_missions", ["phase"])
        op.create_index("ix_weekly_missions_pattern_code", "weekly_missions", ["pattern_code"])
        op.create_index("ix_weekly_missions_status", "weekly_missions", ["status"])

    if not has_table(inspector, "weekly_mission_items"):
        op.create_table(
            "weekly_mission_items",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("weekly_mission_id", sa.Integer(), sa.ForeignKey("weekly_missions.id"), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=False),
            sa.Column("target_count", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("current_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        )
        op.create_index("ix_weekly_mission_items_weekly_mission_id", "weekly_mission_items", ["weekly_mission_id"])
        op.create_index("ix_weekly_mission_items_status", "weekly_mission_items", ["status"])

    if not has_table(inspector, "test_records"):
        op.create_table(
            "test_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("test_type", sa.String(length=20), nullable=False),
            sa.Column("test_date", sa.Date(), nullable=False),
            sa.Column("overall_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("listening_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("reading_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("writing_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("speaking_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("cefr_level", sa.String(length=20), nullable=False, server_default=""),
            sa.Column("note", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_test_records_player_id", "test_records", ["player_id"])
        op.create_index("ix_test_records_test_type", "test_records", ["test_type"])
        op.create_index("ix_test_records_test_date", "test_records", ["test_date"])
        op.create_index("ix_test_records_created_at", "test_records", ["created_at"])

    if not has_table(inspector, "skill_rank_suggestions"):
        op.create_table(
            "skill_rank_suggestions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("source_test_record_id", sa.Integer(), sa.ForeignKey("test_records.id"), nullable=True),
            sa.Column("current_rank", sa.String(length=2), nullable=False, server_default="F"),
            sa.Column("suggested_rank", sa.String(length=2), nullable=False, server_default="F"),
            sa.Column("direction", sa.String(length=10), nullable=False, server_default="same"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_skill_rank_suggestions_skill_id", "skill_rank_suggestions", ["skill_id"])
        op.create_index("ix_skill_rank_suggestions_source_test_record_id", "skill_rank_suggestions", ["source_test_record_id"])
        op.create_index("ix_skill_rank_suggestions_status", "skill_rank_suggestions", ["status"])
        op.create_index("ix_skill_rank_suggestions_created_at", "skill_rank_suggestions", ["created_at"])

    if not has_table(inspector, "skill_rank_history"):
        op.create_table(
            "skill_rank_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("old_rank", sa.String(length=2), nullable=False, server_default="F"),
            sa.Column("new_rank", sa.String(length=2), nullable=False, server_default="F"),
            sa.Column("source_test_record_id", sa.Integer(), sa.ForeignKey("test_records.id"), nullable=True),
            sa.Column("change_reason", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("changed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_skill_rank_history_skill_id", "skill_rank_history", ["skill_id"])
        op.create_index("ix_skill_rank_history_source_test_record_id", "skill_rank_history", ["source_test_record_id"])
        op.create_index("ix_skill_rank_history_changed_at", "skill_rank_history", ["changed_at"])

    if not has_table(inspector, "error_logs"):
        op.create_table(
            "error_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("source", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("error_description", sa.Text(), nullable=False),
            sa.Column("correction", sa.Text(), nullable=False),
            sa.Column("cause", sa.Text(), nullable=False),
            sa.Column("prevention", sa.Text(), nullable=False),
            sa.Column("error_tag", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("logged_date", sa.Date(), nullable=False),
        )
        op.create_index("ix_error_logs_campaign_id", "error_logs", ["campaign_id"])
        op.create_index("ix_error_logs_skill_id", "error_logs", ["skill_id"])
        op.create_index("ix_error_logs_error_tag", "error_logs", ["error_tag"])
        op.create_index("ix_error_logs_logged_date", "error_logs", ["logged_date"])

    if not has_table(inspector, "writing_entries"):
        op.create_table(
            "writing_entries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("task_type", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("prompt", sa.Text(), nullable=False),
            sa.Column("draft_text", sa.Text(), nullable=False),
            sa.Column("self_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("estimated_band", sa.String(length=20), nullable=False, server_default=""),
            sa.Column("feedback_note", sa.Text(), nullable=False),
            sa.Column("revised_text", sa.Text(), nullable=False),
            sa.Column("entry_date", sa.Date(), nullable=False),
        )
        op.create_index("ix_writing_entries_campaign_id", "writing_entries", ["campaign_id"])
        op.create_index("ix_writing_entries_entry_date", "writing_entries", ["entry_date"])

    if not has_table(inspector, "speaking_entries"):
        op.create_table(
            "speaking_entries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("part", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("topic", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("cue_or_question", sa.Text(), nullable=False),
            sa.Column("self_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("self_note", sa.Text(), nullable=False),
            sa.Column("transcript_summary", sa.Text(), nullable=False),
            sa.Column("entry_date", sa.Date(), nullable=False),
        )
        op.create_index("ix_speaking_entries_campaign_id", "speaking_entries", ["campaign_id"])
        op.create_index("ix_speaking_entries_entry_date", "speaking_entries", ["entry_date"])

    if not has_table(inspector, "mock_tests"):
        op.create_table(
            "mock_tests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("test_type", sa.String(length=80), nullable=False, server_default=""),
            sa.Column("scope", sa.String(length=20), nullable=False, server_default="full"),
            sa.Column("source", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("raw_score", sa.String(length=50), nullable=False, server_default=""),
            sa.Column("estimated_band", sa.String(length=20), nullable=False, server_default=""),
            sa.Column("estimated_band_override", sa.String(length=20), nullable=False, server_default=""),
            sa.Column("note", sa.Text(), nullable=False),
            sa.Column("test_date", sa.Date(), nullable=False),
        )
        op.create_index("ix_mock_tests_campaign_id", "mock_tests", ["campaign_id"])
        op.create_index("ix_mock_tests_test_type", "mock_tests", ["test_type"])
        op.create_index("ix_mock_tests_scope", "mock_tests", ["scope"])
        op.create_index("ix_mock_tests_test_date", "mock_tests", ["test_date"])

    if not has_table(inspector, "weakness_suggestions"):
        op.create_table(
            "weakness_suggestions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
            sa.Column("source_type", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("source_ref_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("detail", sa.Text(), nullable=False),
            sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_weakness_suggestions_skill_id", "weakness_suggestions", ["skill_id"])
        op.create_index("ix_weakness_suggestions_source_type", "weakness_suggestions", ["source_type"])
        op.create_index("ix_weakness_suggestions_status", "weakness_suggestions", ["status"])
        op.create_index("ix_weakness_suggestions_created_at", "weakness_suggestions", ["created_at"])


def migrate_existing_rows() -> None:
    bind = op.get_bind()
    players = bind.execute(text("SELECT id, start_date FROM players")).mappings().all()

    for player in players:
        existing_campaign = bind.execute(
            text("SELECT id FROM campaigns WHERE player_id = :player_id ORDER BY id LIMIT 1"),
            {"player_id": player["id"]},
        ).scalar()
        if existing_campaign:
            campaign_id = existing_campaign
        else:
            start_date = player["start_date"] or date(2026, 6, 4)
            end_date = start_date + timedelta(days=18 * 30)
            bind.execute(
                text(
                    """
                    INSERT INTO campaigns (player_id, start_date, end_date, status, created_at)
                    VALUES (:player_id, :start_date, :end_date, 'active', NOW())
                    """
                ),
                {"player_id": player["id"], "start_date": start_date, "end_date": end_date},
            )
            campaign_id = bind.execute(text("SELECT LAST_INSERT_ID()")).scalar()

        bind.execute(
            text("UPDATE players SET active_campaign_id = :campaign_id WHERE id = :player_id AND active_campaign_id IS NULL"),
            {"campaign_id": campaign_id, "player_id": player["id"]},
        )

        bind.execute(
            text(
                """
                UPDATE quests
                SET campaign_id = :campaign_id
                WHERE campaign_id IS NULL
                """
            ),
            {"campaign_id": campaign_id},
        )
        bind.execute(
            text(
                """
                UPDATE boss_battles
                SET campaign_id = :campaign_id
                WHERE campaign_id IS NULL
                """
            ),
            {"campaign_id": campaign_id},
        )

    bind.execute(
        text(
            """
            UPDATE skills
            SET confirmed_rank = rank
            WHERE confirmed_rank IS NULL OR confirmed_rank = ''
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE checkins
            SET focus = 3
            WHERE focus IS NULL
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE quests
            SET status = CASE
                WHEN completed = 1 THEN 'completed'
                WHEN quest_date < CURDATE() AND DATEDIFF(CURDATE(), quest_date) <= 3 THEN 'overdue'
                WHEN quest_date < CURDATE() AND DATEDIFF(CURDATE(), quest_date) > 3 THEN 'expired'
                ELSE 'pending'
            END
            WHERE status IS NULL OR status = ''
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE quests
            SET earned_xp = CASE
                WHEN completed = 1 THEN xp
                ELSE 0
            END
            WHERE earned_xp IS NULL
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE quests
            SET base_xp = xp
            WHERE base_xp IS NULL OR base_xp = 0
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE quests
            SET quest_role = CASE
                WHEN session_type = 'Main Quest' THEN 'core'
                WHEN session_type = 'Daily Quest' THEN 'support'
                ELSE 'mini'
            END
            WHERE quest_role IS NULL OR quest_role = ''
            """
        )
    )
    bind.execute(
        text(
            """
            UPDATE quests
            SET difficulty = CASE
                WHEN xp >= 40 THEN 'hard'
                WHEN xp >= 20 THEN 'normal'
                ELSE 'easy'
            END
            WHERE difficulty IS NULL OR difficulty = ''
            """
        )
    )


def upgrade() -> None:
    create_tables()

    ensure_column("players", sa.Column("display_name", sa.String(length=120), nullable=False, server_default="IELTS Hunter"))
    ensure_column("players", sa.Column("target_overall_band", sa.String(length=20), nullable=False, server_default="7.0-7.5"))
    ensure_column("players", sa.Column("current_estimated_level", sa.String(length=50), nullable=False, server_default="B1"))
    ensure_column("players", sa.Column("strongest_skill", sa.String(length=80), nullable=False, server_default="Listening"))
    ensure_column("players", sa.Column("weakest_skill", sa.String(length=80), nullable=False, server_default="Reading"))
    ensure_column("players", sa.Column("study_days_per_week", sa.Integer(), nullable=False, server_default="4"))
    ensure_column("players", sa.Column("session_minutes", sa.Integer(), nullable=False, server_default="120"))
    ensure_column("players", sa.Column("daily_mini_study_minutes", sa.Integer(), nullable=False, server_default="20"))
    ensure_column("players", sa.Column("player_xp", sa.Integer(), nullable=False, server_default="0"))
    ensure_column("players", sa.Column("player_level", sa.Integer(), nullable=False, server_default="1"))
    ensure_column("players", sa.Column("player_rank", sa.String(length=2), nullable=False, server_default="F"))
    ensure_column("players", sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"))
    ensure_column("players", sa.Column("best_streak", sa.Integer(), nullable=False, server_default="0"))
    ensure_column("players", sa.Column("shield_count", sa.Integer(), nullable=False, server_default="1"))
    ensure_column("players", sa.Column("shield_regen_progress", sa.Integer(), nullable=False, server_default="0"))
    ensure_column("players", sa.Column("perfect_day_count", sa.Integer(), nullable=False, server_default="0"))
    ensure_column("players", sa.Column("setup_completed", sa.Boolean(), nullable=False, server_default=sa.false()))
    ensure_column("players", sa.Column("active_campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True))
    ensure_index("players", "ix_players_active_campaign_id", ["active_campaign_id"])

    ensure_column("skills", sa.Column("confirmed_rank", sa.String(length=2), nullable=False, server_default="F"))
    ensure_column("skills", sa.Column("user_weakness_note", sa.Text(), nullable=False, server_default=""))
    ensure_column("skills", sa.Column("last_system_suggestion_at", sa.DateTime(), nullable=True))
    ensure_index("skills", "ix_skills_confirmed_rank", ["confirmed_rank"])
    ensure_index("skills", "ix_skills_last_practiced", ["last_practiced"])
    ensure_index("skills", "ix_skills_last_system_suggestion_at", ["last_system_suggestion_at"])

    ensure_column("quests", sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True))
    ensure_column("quests", sa.Column("template_id", sa.Integer(), sa.ForeignKey("quest_templates.id"), nullable=True))
    ensure_column("quests", sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"))
    ensure_column("quests", sa.Column("quest_role", sa.String(length=20), nullable=False, server_default="mini"))
    ensure_column("quests", sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="easy"))
    ensure_column("quests", sa.Column("base_xp", sa.Integer(), nullable=False, server_default="10"))
    ensure_column("quests", sa.Column("earned_xp", sa.Integer(), nullable=True))
    ensure_column("quests", sa.Column("completed_mode", sa.String(length=20), nullable=True))
    ensure_column("quests", sa.Column("completion_note", sa.String(length=255), nullable=False, server_default=""))
    ensure_column("quests", sa.Column("raw_score", sa.String(length=120), nullable=False, server_default=""))
    ensure_column("quests", sa.Column("tracker_type", sa.String(length=40), nullable=False, server_default=""))
    ensure_column("quests", sa.Column("tracker_entry_id", sa.Integer(), nullable=True))
    ensure_column("quests", sa.Column("expired_at", sa.DateTime(), nullable=True))
    ensure_index("quests", "ix_quests_campaign_id", ["campaign_id"])
    ensure_index("quests", "ix_quests_template_id", ["template_id"])
    ensure_index("quests", "ix_quests_status", ["status"])
    ensure_index("quests", "ix_quests_quest_role", ["quest_role"])
    ensure_index("quests", "ix_quests_difficulty", ["difficulty"])

    ensure_column("checkins", sa.Column("focus", sa.Integer(), nullable=True))

    ensure_column("boss_battles", sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=True))
    ensure_column("boss_battles", sa.Column("month_index", sa.Integer(), nullable=False, server_default="1"))
    ensure_column("boss_battles", sa.Column("reward_xp", sa.Integer(), nullable=False, server_default="0"))
    ensure_column("boss_battles", sa.Column("badge_id", sa.Integer(), sa.ForeignKey("badges.id"), nullable=True))
    ensure_column("boss_battles", sa.Column("result_status", sa.String(length=20), nullable=False, server_default="locked"))
    ensure_column("boss_battles", sa.Column("result_note", sa.String(length=255), nullable=False, server_default=""))
    ensure_column("boss_battles", sa.Column("practice_suggestion", sa.String(length=255), nullable=False, server_default=""))
    ensure_column("boss_battles", sa.Column("cleared_at", sa.DateTime(), nullable=True))
    ensure_index("boss_battles", "ix_boss_battles_campaign_id", ["campaign_id"])
    ensure_index("boss_battles", "ix_boss_battles_month_index", ["month_index"])
    ensure_index("boss_battles", "ix_boss_battles_result_status", ["result_status"])

    migrate_existing_rows()


def downgrade() -> None:
    pass
