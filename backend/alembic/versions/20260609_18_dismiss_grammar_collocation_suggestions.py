"""dismiss pending Grammar and Collocation rank suggestions (data migration)

Revision ID: 20260609_18
Revises: 20260609_17
Create Date: 2026-06-09
"""

from alembic import op

revision = "20260609_18"
down_revision = "20260609_17"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Grammar and Collocation are support sources, not matrix skills.
    # Any pending suggestions for them were created by the old inferred dict
    # and must be dismissed so they no longer appear in the inbox.
    op.execute(
        """
        UPDATE skill_rank_suggestions
        SET status = 'dismissed', resolved_at = NOW()
        WHERE status = 'pending'
          AND skill_id IN (
              SELECT id FROM skills WHERE name IN ('Grammar', 'Collocation')
          )
        """
    )


def downgrade() -> None:
    # Cannot reliably un-dismiss — these rows were created by a now-removed
    # code path. Downgrade is intentionally a no-op.
    pass
