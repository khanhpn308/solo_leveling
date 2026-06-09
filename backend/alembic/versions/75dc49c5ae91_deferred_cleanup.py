"""deferred_cleanup

Revision ID: 75dc49c5ae91
Revises: 6c233774a1db
Create Date: 2026-06-07 03:27:19.904115

This migration drops legacy mutable-state columns from skills, quests,
weakness_suggestions, and badges. Index renames are intentionally skipped
because the old idx_ indexes are required by existing foreign key constraints
and renaming is cosmetic only.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '75dc49c5ae91'
down_revision = '6c233774a1db'
branch_labels = None
depends_on = None


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    return any(i['name'] == index_name for i in inspector.get_indexes(table_name))


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    return any(c['name'] == column_name for c in inspector.get_columns(table_name))


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _drop_index_if_exists(inspector, table_name: str, index_name: str) -> None:
    if _has_index(inspector, table_name, index_name):
        try:
            op.drop_index(index_name, table_name=table_name)
        except Exception:
            pass  # silently skip if FK constraint prevents drop


def _create_index_if_missing(inspector, index_name: str, table_name: str, columns: list, unique: bool = False) -> None:
    if not _has_index(inspector, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def _drop_column_if_exists(inspector, table_name: str, column_name: str) -> None:
    if _has_column(inspector, table_name, column_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    # badge_unlocks: create ix_badge_unlocks_id if missing
    if _has_table(insp, 'badge_unlocks'):
        _create_index_if_missing(insp, 'ix_badge_unlocks_id', 'badge_unlocks', ['id'])

    # badges: drop legacy unlock columns
    if _has_table(insp, 'badges'):
        _drop_column_if_exists(insp, 'badges', 'unlocked_at')
        _drop_column_if_exists(insp, 'badges', 'unlocked')

    # campaign_skill_states: create id index if missing
    if _has_table(insp, 'campaign_skill_states'):
        _create_index_if_missing(insp, 'ix_campaign_skill_states_id', 'campaign_skill_states', ['id'])

    # quests: drop legacy tracker columns
    if _has_table(insp, 'quests'):
        _drop_column_if_exists(insp, 'quests', 'tracker_entry_id')
        _drop_column_if_exists(insp, 'quests', 'tracker_type')

    # skills: drop legacy mutable state columns + their indexes
    if _has_table(insp, 'skills'):
        _drop_index_if_exists(insp, 'skills', 'ix_skills_confirmed_rank')
        _drop_index_if_exists(insp, 'skills', 'ix_skills_last_practiced')
        _drop_index_if_exists(insp, 'skills', 'ix_skills_last_system_suggestion_at')
        _drop_column_if_exists(insp, 'skills', 'rank')
        _drop_column_if_exists(insp, 'skills', 'last_system_suggestion_at')
        _drop_column_if_exists(insp, 'skills', 'user_weakness_note')
        _drop_column_if_exists(insp, 'skills', 'xp')
        _drop_column_if_exists(insp, 'skills', 'level')
        _drop_column_if_exists(insp, 'skills', 'streak')
        _drop_column_if_exists(insp, 'skills', 'last_practiced')
        _drop_column_if_exists(insp, 'skills', 'weak_point')
        _drop_column_if_exists(insp, 'skills', 'confirmed_rank')

    # weakness_suggestions: drop legacy source columns
    if _has_table(insp, 'weakness_suggestions'):
        _drop_index_if_exists(insp, 'weakness_suggestions', 'ix_weakness_suggestions_source_type')
        _drop_column_if_exists(insp, 'weakness_suggestions', 'source_type')
        _drop_column_if_exists(insp, 'weakness_suggestions', 'source_ref_id')

    # NOTE: vocabulary table index renames (idx_ -> ix_) are intentionally
    # skipped here because those old indexes support FK constraints in MySQL
    # and dropping them would require temporarily dropping/re-adding the FKs.
    # The old idx_ names are cosmetic only and do not affect query performance.


def downgrade() -> None:
    # Downgrade is intentionally minimal – legacy columns are not restored.
    pass
