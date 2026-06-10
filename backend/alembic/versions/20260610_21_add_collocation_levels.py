"""add collocation_levels table and level_id FK on collocation_collections

Revision ID: 20260610_21
Revises: 20260609_20
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa

revision = "20260610_21"
down_revision = "20260609_20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collocation_levels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("difficulty_order", sa.Integer(), nullable=False),
        sa.Column("icon", sa.String(10), nullable=False, server_default="📕"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_collocation_levels_difficulty_order",
        "collocation_levels",
        ["difficulty_order"],
    )

    op.add_column(
        "collocation_collections",
        sa.Column(
            "level_id",
            sa.Integer(),
            sa.ForeignKey("collocation_levels.id", name="fk_colcol_level_id"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_collocation_collections_level_id",
        "collocation_collections",
        ["level_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_collocation_collections_level_id", table_name="collocation_collections")
    op.drop_column("collocation_collections", "level_id")

    op.drop_index("ix_collocation_levels_difficulty_order", table_name="collocation_levels")
    op.drop_table("collocation_levels")
