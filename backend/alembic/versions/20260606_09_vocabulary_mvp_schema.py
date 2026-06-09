"""add vocabulary mvp tables

Revision ID: 20260606_09
Revises: 20260606_08
Create Date: 2026-06-06 23:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260606_09"
down_revision = "20260606_08"
branch_labels = None
depends_on = None


def has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if not has_table(inspector, "vocabulary_items"):
        op.create_table(
            "vocabulary_items",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("word", sa.String(length=255), nullable=False),
            sa.Column("normalized_word", sa.String(length=255), nullable=True),
            sa.Column("part_of_speech", sa.String(length=50), nullable=True),
            sa.Column("cefr_level", sa.String(length=10), nullable=True),
            sa.Column("ielts_topic", sa.String(length=100), nullable=True),
            sa.Column("meaning_en", sa.Text(), nullable=True),
            sa.Column("meaning_vi", sa.Text(), nullable=True),
            sa.Column("register_label", sa.String(length=50), nullable=True),
            sa.Column("grammar_note", sa.Text(), nullable=True),
            sa.Column("pronunciation_ipa", sa.String(length=255), nullable=True),
            sa.Column("word_stress", sa.String(length=255), nullable=True),
            sa.Column("source_type", sa.String(length=50), nullable=True),
            sa.Column("source_reference", sa.String(length=255), nullable=True),
            sa.Column("mastery_rank", sa.String(length=5), nullable=False, server_default="F"),
            sa.Column("mastery_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_items_player_id", "vocabulary_items", ["player_id"])
        op.create_index("idx_vocabulary_items_topic", "vocabulary_items", ["ielts_topic"])
        op.create_index("idx_vocabulary_items_rank", "vocabulary_items", ["mastery_rank"])
        op.create_index("idx_vocabulary_items_word", "vocabulary_items", ["normalized_word"])

    if not has_table(inspector, "vocabulary_examples"):
        op.create_table(
            "vocabulary_examples",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("vocabulary_item_id", sa.BigInteger(), sa.ForeignKey("vocabulary_items.id"), nullable=False),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("example_sentence", sa.Text(), nullable=False),
            sa.Column("example_type", sa.String(length=50), nullable=True),
            sa.Column("is_corrected", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
            sa.Column("correction_note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_examples_item_id", "vocabulary_examples", ["vocabulary_item_id"])
        op.create_index("idx_vocabulary_examples_player_id", "vocabulary_examples", ["player_id"])

    if not has_table(inspector, "vocabulary_collocations"):
        op.create_table(
            "vocabulary_collocations",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("vocabulary_item_id", sa.BigInteger(), sa.ForeignKey("vocabulary_items.id"), nullable=False),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("collocation", sa.String(length=255), nullable=False),
            sa.Column("collocation_type", sa.String(length=100), nullable=True),
            sa.Column("example_sentence", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_collocations_item_id", "vocabulary_collocations", ["vocabulary_item_id"])
        op.create_index("idx_vocabulary_collocations_player_id", "vocabulary_collocations", ["player_id"])

    if not has_table(inspector, "vocabulary_relations"):
        op.create_table(
            "vocabulary_relations",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("source_word_id", sa.BigInteger(), sa.ForeignKey("vocabulary_items.id"), nullable=False),
            sa.Column("target_word_id", sa.BigInteger(), sa.ForeignKey("vocabulary_items.id"), nullable=True),
            sa.Column("target_text", sa.String(length=255), nullable=True),
            sa.Column("relation_type", sa.String(length=50), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_vocabulary_relations_player_id", "vocabulary_relations", ["player_id"])
        op.create_index("idx_vocabulary_relations_source_id", "vocabulary_relations", ["source_word_id"])
        op.create_index("idx_vocabulary_relations_target_id", "vocabulary_relations", ["target_word_id"])

    if not has_table(inspector, "flashcards"):
        op.create_table(
            "flashcards",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("vocabulary_item_id", sa.BigInteger(), sa.ForeignKey("vocabulary_items.id"), nullable=False),
            sa.Column("card_type", sa.String(length=50), nullable=True),
            sa.Column("front_text", sa.Text(), nullable=False),
            sa.Column("back_text", sa.Text(), nullable=False),
            sa.Column("hint", sa.Text(), nullable=True),
            sa.Column("difficulty", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_flashcards_player_id", "flashcards", ["player_id"])
        op.create_index("idx_flashcards_item_id", "flashcards", ["vocabulary_item_id"])

    if not has_table(inspector, "spaced_repetition_state"):
        op.create_table(
            "spaced_repetition_state",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
            sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
            sa.Column("flashcard_id", sa.BigInteger(), sa.ForeignKey("flashcards.id"), nullable=False),
            sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
            sa.Column("interval_days", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("repetition_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("last_reviewed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_spaced_repetition_player_id", "spaced_repetition_state", ["player_id"])
        op.create_index("idx_spaced_repetition_flashcard_id", "spaced_repetition_state", ["flashcard_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if has_table(inspector, "spaced_repetition_state"):
        op.drop_table("spaced_repetition_state")
    if has_table(inspector, "flashcards"):
        op.drop_table("flashcards")
    if has_table(inspector, "vocabulary_relations"):
        op.drop_table("vocabulary_relations")
    if has_table(inspector, "vocabulary_collocations"):
        op.drop_table("vocabulary_collocations")
    if has_table(inspector, "vocabulary_examples"):
        op.drop_table("vocabulary_examples")
    if has_table(inspector, "vocabulary_items"):
        op.drop_table("vocabulary_items")
