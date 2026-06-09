"""add collocation_flashcards table

Revision ID: 20260609_20
Revises: 20260609_19
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa

revision = "20260609_20"
down_revision = "20260609_19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collocation_flashcards",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False, index=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False, index=True),
        sa.Column("collocation_item_id", sa.Integer(), sa.ForeignKey("collocation_items.id"), nullable=False, index=True),
        sa.Column("familiarity", sa.String(10), nullable=False, server_default="again"),
        sa.Column("familiarity_set_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("player_id", "campaign_id", "collocation_item_id", name="uq_collocation_flashcard"),
    )


def downgrade() -> None:
    op.drop_table("collocation_flashcards")
