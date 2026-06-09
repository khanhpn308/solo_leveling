"""add typed links check constraints

Revision ID: 089adadeddde
Revises: 20260607_14
Create Date: 2026-06-07 06:24:00.092730
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '089adadeddde'
down_revision = '20260607_14'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_quests_only_one_tracker",
        "quests",
        "(CASE WHEN error_log_id IS NULL THEN 1 ELSE 0 END + "
        "CASE WHEN writing_entry_id IS NULL THEN 1 ELSE 0 END + "
        "CASE WHEN speaking_entry_id IS NULL THEN 1 ELSE 0 END + "
        "CASE WHEN mock_test_id IS NULL THEN 1 ELSE 0 END) >= 3"
    )
    op.create_check_constraint(
        "ck_weakness_suggestions_only_one_source",
        "weakness_suggestions",
        "(CASE WHEN source_test_record_id IS NULL THEN 1 ELSE 0 END + "
        "CASE WHEN source_mock_test_id IS NULL THEN 1 ELSE 0 END + "
        "CASE WHEN source_error_log_id IS NULL THEN 1 ELSE 0 END + "
        "CASE WHEN source_quest_id IS NULL THEN 1 ELSE 0 END) >= 3"
    )


def downgrade() -> None:
    op.drop_constraint("ck_quests_only_one_tracker", "quests", type_="check")
    op.drop_constraint("ck_weakness_suggestions_only_one_source", "weakness_suggestions", type_="check")
