"""Add study plan week/session tables for main quests.

Revision ID: 20260603_03
Revises: 20260603_02
Create Date: 2026-06-03 23:55:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260603_03"
down_revision = "20260603_02"
branch_labels = None
depends_on = None


def has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def has_column(inspector, table_name: str, column_name: str) -> bool:
    if not has_table(inspector, table_name):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def has_index(inspector, table_name: str, index_name: str) -> bool:
    if not has_table(inspector, table_name):
        return False
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def ensure_column(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not has_column(inspector, table_name, column.name):
        op.add_column(table_name, column)


def ensure_index(table_name: str, index_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not has_index(inspector, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def create_tables() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not has_table(inspector, "study_plan_weeks"):
        op.create_table(
            "study_plan_weeks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("phase_id", sa.Integer(), sa.ForeignKey("roadmap_phases.id"), nullable=False),
            sa.Column("week_no", sa.Integer(), nullable=False),
            sa.Column("week_start", sa.Date(), nullable=False),
            sa.Column("week_end", sa.Date(), nullable=False),
            sa.Column("weekly_focus", sa.Text(), nullable=False),
            sa.Column("weekly_output", sa.Text(), nullable=False),
            sa.Column("material_summary", sa.Text(), nullable=False),
            sa.Column("mini_task", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("campaign_id", "week_no", name="uq_study_plan_week_campaign_week"),
        )
        op.create_index("ix_study_plan_weeks_campaign_id", "study_plan_weeks", ["campaign_id"])
        op.create_index("ix_study_plan_weeks_phase_id", "study_plan_weeks", ["phase_id"])
        op.create_index("ix_study_plan_weeks_week_no", "study_plan_weeks", ["week_no"])
        op.create_index("ix_study_plan_weeks_week_start", "study_plan_weeks", ["week_start"])
        op.create_index("ix_study_plan_weeks_week_end", "study_plan_weeks", ["week_end"])
        op.create_index("ix_study_plan_weeks_created_at", "study_plan_weeks", ["created_at"])

    if not has_table(inspector, "study_plan_sessions"):
        op.create_table(
            "study_plan_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
            sa.Column("phase_id", sa.Integer(), sa.ForeignKey("roadmap_phases.id"), nullable=False),
            sa.Column("study_plan_week_id", sa.Integer(), sa.ForeignKey("study_plan_weeks.id"), nullable=False),
            sa.Column("week_no", sa.Integer(), nullable=False),
            sa.Column("session_no", sa.Integer(), nullable=False),
            sa.Column("study_date", sa.Date(), nullable=False),
            sa.Column("weekday_label", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("session_label", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("skill_summary", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("task_detail", sa.Text(), nullable=False),
            sa.Column("material_summary", sa.Text(), nullable=False),
            sa.Column("deliverable", sa.Text(), nullable=False),
            sa.Column("status_text", sa.String(length=40), nullable=False, server_default=""),
            sa.Column("note_text", sa.Text(), nullable=False),
            sa.Column("mini_task", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("study_plan_week_id", "session_no", name="uq_study_plan_session_week_no"),
        )
        op.create_index("ix_study_plan_sessions_campaign_id", "study_plan_sessions", ["campaign_id"])
        op.create_index("ix_study_plan_sessions_phase_id", "study_plan_sessions", ["phase_id"])
        op.create_index("ix_study_plan_sessions_study_plan_week_id", "study_plan_sessions", ["study_plan_week_id"])
        op.create_index("ix_study_plan_sessions_week_no", "study_plan_sessions", ["week_no"])
        op.create_index("ix_study_plan_sessions_session_no", "study_plan_sessions", ["session_no"])
        op.create_index("ix_study_plan_sessions_study_date", "study_plan_sessions", ["study_date"])
        op.create_index("ix_study_plan_sessions_created_at", "study_plan_sessions", ["created_at"])


def upgrade() -> None:
    create_tables()
    ensure_column("quests", sa.Column("study_plan_week_id", sa.Integer(), sa.ForeignKey("study_plan_weeks.id"), nullable=True))
    ensure_column("quests", sa.Column("study_plan_session_id", sa.Integer(), sa.ForeignKey("study_plan_sessions.id"), nullable=True))
    ensure_index("quests", "ix_quests_study_plan_week_id", ["study_plan_week_id"])
    ensure_index("quests", "ix_quests_study_plan_session_id", ["study_plan_session_id"])


def downgrade() -> None:
    pass
