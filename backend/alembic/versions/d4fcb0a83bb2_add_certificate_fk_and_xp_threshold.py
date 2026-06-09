"""add_certificate_fk_and_xp_threshold

Revision ID: d4fcb0a83bb2
Revises: 30b9013e0a20
Create Date: 2026-06-07 18:09:03.071970
"""
from alembic import op
import sqlalchemy as sa
import datetime


# revision identifiers, used by Alembic.
revision = 'd4fcb0a83bb2'
down_revision = '30b9013e0a20'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    def _col_exists(table, col):
        r = conn.execute(sa.text(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME=:c LIMIT 1"
        ), {"t": table, "c": col})
        return r.fetchone() is not None

    def _fk_exists(table, constraint_name):
        r = conn.execute(sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND CONSTRAINT_NAME=:c AND CONSTRAINT_TYPE='FOREIGN KEY' LIMIT 1"
        ), {"t": table, "c": constraint_name})
        return r.fetchone() is not None

    # Add source_certificate_record_id FK to suggestions
    if not _col_exists('skill_rank_suggestions', 'source_certificate_record_id'):
        op.add_column('skill_rank_suggestions', sa.Column('source_certificate_record_id', sa.Integer(), nullable=True))
    if not _fk_exists('skill_rank_suggestions', 'fk_skill_rank_suggestions_certificate'):
        op.create_foreign_key('fk_skill_rank_suggestions_certificate', 'skill_rank_suggestions', 'certificate_records', ['source_certificate_record_id'], ['id'])
        
    # Add source_certificate_record_id FK to history
    if not _col_exists('skill_rank_history', 'source_certificate_record_id'):
        op.add_column('skill_rank_history', sa.Column('source_certificate_record_id', sa.Integer(), nullable=True))
    if not _fk_exists('skill_rank_history', 'fk_skill_rank_history_certificate'):
        op.create_foreign_key('fk_skill_rank_history_certificate', 'skill_rank_history', 'certificate_records', ['source_certificate_record_id'], ['id'])

    # Find Vocabulary skill dynamically to avoid FK constraint fails on seed
    r = conn.execute(sa.text("SELECT id FROM skills WHERE name='Vocabulary' LIMIT 1"))
    vocab_skill = r.fetchone()
    if vocab_skill:
        vocab_skill_id = vocab_skill[0]
        # Seed XP thresholds for rank_exam_pools if not already seeded for this skill
        r = conn.execute(sa.text("SELECT COUNT(*) FROM rank_exam_pools WHERE skill_id=:s"), {"s": vocab_skill_id})
        count = r.scalar()
        if count == 0:
            now = datetime.datetime.utcnow()
            rank_exam_pool_table = sa.table('rank_exam_pools',
                sa.column('skill_id', sa.Integer),
                sa.column('from_rank', sa.String),
                sa.column('to_rank', sa.String),
                sa.column('title', sa.String),
                sa.column('xp_threshold', sa.Integer),
                sa.column('is_active', sa.Boolean),
                sa.column('pass_percent', sa.Integer),
                sa.column('default_time_limit_minutes', sa.Integer),
                sa.column('max_attempts_per_day', sa.Integer),
                sa.column('created_at', sa.DateTime),
                sa.column('updated_at', sa.DateTime),
            )
            op.bulk_insert(rank_exam_pool_table, [
                {'skill_id': vocab_skill_id, 'from_rank': 'F', 'to_rank': 'E', 'title': 'F to E', 'xp_threshold': 500, 'is_active': True, 'pass_percent': 80, 'default_time_limit_minutes': 30, 'max_attempts_per_day': 2, 'created_at': now, 'updated_at': now},
                {'skill_id': vocab_skill_id, 'from_rank': 'E', 'to_rank': 'D', 'title': 'E to D', 'xp_threshold': 1200, 'is_active': True, 'pass_percent': 80, 'default_time_limit_minutes': 30, 'max_attempts_per_day': 2, 'created_at': now, 'updated_at': now},
                {'skill_id': vocab_skill_id, 'from_rank': 'D', 'to_rank': 'C', 'title': 'D to C', 'xp_threshold': 2500, 'is_active': True, 'pass_percent': 80, 'default_time_limit_minutes': 30, 'max_attempts_per_day': 2, 'created_at': now, 'updated_at': now},
                {'skill_id': vocab_skill_id, 'from_rank': 'C', 'to_rank': 'B', 'title': 'C to B', 'xp_threshold': 4500, 'is_active': True, 'pass_percent': 80, 'default_time_limit_minutes': 30, 'max_attempts_per_day': 2, 'created_at': now, 'updated_at': now},
                {'skill_id': vocab_skill_id, 'from_rank': 'B', 'to_rank': 'A', 'title': 'B to A', 'xp_threshold': 7000, 'is_active': True, 'pass_percent': 80, 'default_time_limit_minutes': 30, 'max_attempts_per_day': 2, 'created_at': now, 'updated_at': now},
                {'skill_id': vocab_skill_id, 'from_rank': 'A', 'to_rank': 'S', 'title': 'A to S', 'xp_threshold': 10000, 'is_active': True, 'pass_percent': 80, 'default_time_limit_minutes': 30, 'max_attempts_per_day': 2, 'created_at': now, 'updated_at': now},
            ])
    
    op.alter_column('rank_exam_pools', 'xp_threshold', server_default=None)


def downgrade() -> None:
    conn = op.get_bind()

    def _col_exists(table, col):
        r = conn.execute(sa.text(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME=:c LIMIT 1"
        ), {"t": table, "c": col})
        return r.fetchone() is not None

    def _fk_exists(table, constraint_name):
        r = conn.execute(sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND CONSTRAINT_NAME=:c AND CONSTRAINT_TYPE='FOREIGN KEY' LIMIT 1"
        ), {"t": table, "c": constraint_name})
        return r.fetchone() is not None

    # Drop foreign keys and columns for history
    if _fk_exists('skill_rank_history', 'fk_skill_rank_history_certificate'):
        op.drop_constraint('fk_skill_rank_history_certificate', 'skill_rank_history', type_='foreignkey')
    if _col_exists('skill_rank_history', 'source_certificate_record_id'):
        op.drop_column('skill_rank_history', 'source_certificate_record_id')
        
    # Drop foreign keys and columns for suggestions
    if _fk_exists('skill_rank_suggestions', 'fk_skill_rank_suggestions_certificate'):
        op.drop_constraint('fk_skill_rank_suggestions_certificate', 'skill_rank_suggestions', type_='foreignkey')
    if _col_exists('skill_rank_suggestions', 'source_certificate_record_id'):
        op.drop_column('skill_rank_suggestions', 'source_certificate_record_id')
