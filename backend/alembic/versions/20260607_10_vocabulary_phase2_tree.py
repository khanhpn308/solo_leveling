"""add vocabulary phase 2 tree tables

Revision ID: 20260607_10
Revises: 20260606_09
Create Date: 2026-06-07 00:10:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260607_10"
down_revision = "20260606_09"
branch_labels = None
depends_on = None


def has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not has_table(inspector, "vocabulary_topics"):
        op.create_table(
            "vocabulary_topics",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("topic_name", sa.String(length=255), nullable=False),
            sa.Column("parent_topic_id", sa.BigInteger(), sa.ForeignKey("vocabulary_topics.id"), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_topics_player_id", "vocabulary_topics", ["player_id"])
        op.create_index("idx_vocabulary_topics_parent_id", "vocabulary_topics", ["parent_topic_id"])

    if not has_table(inspector, "vocabulary_nodes"):
        op.create_table(
            "vocabulary_nodes",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("topic_id", sa.BigInteger(), sa.ForeignKey("vocabulary_topics.id"), nullable=False),
            sa.Column("vocabulary_item_id", sa.BigInteger(), sa.ForeignKey("vocabulary_items.id"), nullable=True),
            sa.Column("node_label", sa.String(length=255), nullable=False),
            sa.Column("node_type", sa.String(length=50), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="locked"),
            sa.Column("x_position", sa.Float(), nullable=True),
            sa.Column("y_position", sa.Float(), nullable=True),
            sa.Column("unlock_requirement", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_nodes_player_id", "vocabulary_nodes", ["player_id"])
        op.create_index("idx_vocabulary_nodes_topic_id", "vocabulary_nodes", ["topic_id"])
        op.create_index("idx_vocabulary_nodes_item_id", "vocabulary_nodes", ["vocabulary_item_id"])

    if not has_table(inspector, "vocabulary_edges"):
        op.create_table(
            "vocabulary_edges",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("source_node_id", sa.BigInteger(), sa.ForeignKey("vocabulary_nodes.id"), nullable=False),
            sa.Column("target_node_id", sa.BigInteger(), sa.ForeignKey("vocabulary_nodes.id"), nullable=False),
            sa.Column("edge_type", sa.String(length=50), nullable=True),
            sa.Column("strength", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_edges_player_id", "vocabulary_edges", ["player_id"])
        op.create_index("idx_vocabulary_edges_source_id", "vocabulary_edges", ["source_node_id"])
        op.create_index("idx_vocabulary_edges_target_id", "vocabulary_edges", ["target_node_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if has_table(inspector, "vocabulary_edges"):
        op.drop_table("vocabulary_edges")
    if has_table(inspector, "vocabulary_nodes"):
        op.drop_table("vocabulary_nodes")
    if has_table(inspector, "vocabulary_topics"):
        op.drop_table("vocabulary_topics")
