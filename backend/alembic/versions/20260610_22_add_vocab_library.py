"""add vocab_library 5-layer schema (vocab_levels, vocab_topics, vocab_units, vocab_sections,
vocab_library_items, vocab_library_flashcards, campaign_vocab_links)

Revision ID: 20260610_22
Revises: 20260610_21
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa

revision = "20260610_22"
down_revision = "20260610_21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. vocab_levels
    op.create_table(
        "vocab_levels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("difficulty_order", sa.Integer(), nullable=False),
        sa.Column("icon", sa.String(10), nullable=False, server_default="📗"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vocab_levels_difficulty_order", "vocab_levels", ["difficulty_order"])

    # 2. vocab_topics
    op.create_table(
        "vocab_topics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("level_id", sa.Integer(), sa.ForeignKey("vocab_levels.id", name="fk_vocab_topics_level_id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("topic_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vocab_topics_level_order", "vocab_topics", ["level_id", "topic_order"])

    # 3. vocab_units
    op.create_table(
        "vocab_units",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("vocab_topics.id", name="fk_vocab_units_topic_id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("unit_number", sa.Integer(), nullable=True),
        sa.Column("unit_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vocab_units_topic_order", "vocab_units", ["topic_id", "unit_order"])

    # 4. vocab_sections
    op.create_table(
        "vocab_sections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("vocab_units.id", name="fk_vocab_sections_unit_id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("section_letter", sa.String(5), nullable=True),
        sa.Column("section_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vocab_sections_unit_order", "vocab_sections", ["unit_id", "section_order"])

    # 5. vocab_library_items
    op.create_table(
        "vocab_library_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("vocab_sections.id", name="fk_vocab_items_section_id"), nullable=False),
        sa.Column("word", sa.String(255), nullable=False),
        sa.Column("part_of_speech", sa.String(80), nullable=True),
        sa.Column("pronunciation_us", sa.String(255), nullable=True),
        sa.Column("meaning_vi", sa.Text(), nullable=True),
        sa.Column("example_en", sa.Text(), nullable=True),
        sa.Column("example_vi", sa.Text(), nullable=True),
        sa.Column("item_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_vocab_library_items_section_order", "vocab_library_items", ["section_id", "item_order"])

    # 6. vocab_library_flashcards
    op.create_table(
        "vocab_library_flashcards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", name="fk_vocab_fc_player"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", name="fk_vocab_fc_campaign"), nullable=False),
        sa.Column("vocab_library_item_id", sa.Integer(), sa.ForeignKey("vocab_library_items.id", name="fk_vocab_fc_item"), nullable=False),
        sa.Column("familiarity", sa.String(10), nullable=False, server_default="again"),
        sa.Column("familiarity_set_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("player_id", "campaign_id", "vocab_library_item_id", name="uq_vocab_library_flashcard"),
    )
    op.create_index("ix_vocab_library_flashcards_player_campaign", "vocab_library_flashcards", ["player_id", "campaign_id"])
    op.create_index("ix_vocab_library_flashcards_item", "vocab_library_flashcards", ["vocab_library_item_id"])

    # 7. campaign_vocab_links
    op.create_table(
        "campaign_vocab_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", name="fk_cvl_campaign"), nullable=False),
        sa.Column("vocab_level_id", sa.Integer(), sa.ForeignKey("vocab_levels.id", name="fk_cvl_vocab_level"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("campaign_id", "vocab_level_id", name="uq_campaign_vocab_link"),
    )
    op.create_index("ix_campaign_vocab_links_campaign", "campaign_vocab_links", ["campaign_id"])


def downgrade() -> None:
    op.drop_table("campaign_vocab_links")

    op.drop_index("ix_vocab_library_flashcards_item", table_name="vocab_library_flashcards")
    op.drop_index("ix_vocab_library_flashcards_player_campaign", table_name="vocab_library_flashcards")
    op.drop_table("vocab_library_flashcards")

    op.drop_index("ix_vocab_library_items_section_order", table_name="vocab_library_items")
    op.drop_table("vocab_library_items")

    op.drop_index("ix_vocab_sections_unit_order", table_name="vocab_sections")
    op.drop_table("vocab_sections")

    op.drop_index("ix_vocab_units_topic_order", table_name="vocab_units")
    op.drop_table("vocab_units")

    op.drop_index("ix_vocab_topics_level_order", table_name="vocab_topics")
    op.drop_table("vocab_topics")

    op.drop_index("ix_vocab_levels_difficulty_order", table_name="vocab_levels")
    op.drop_table("vocab_levels")
