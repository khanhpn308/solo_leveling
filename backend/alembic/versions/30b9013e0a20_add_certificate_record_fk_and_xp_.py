"""add_certificate_record_fk_and_xp_threshold

Revision ID: 30b9013e0a20
Revises: 53902275681a
Create Date: 2026-06-07 10:33:53.755875
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '30b9013e0a20'
down_revision = '53902275681a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Helpers for idempotent checks
    def _idx_exists(table, index_name):
        r = conn.execute(sa.text(
            "SELECT INDEX_NAME FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND INDEX_NAME=:i LIMIT 1"
        ), {"t": table, "i": index_name})
        return r.fetchone() is not None

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

    def _check_exists(table, constraint_name):
        r = conn.execute(sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND CONSTRAINT_NAME=:c AND CONSTRAINT_TYPE='CHECK' LIMIT 1"
        ), {"t": table, "c": constraint_name})
        return r.fetchone() is not None

    def _create_index_if_not_exists(index_name, table, columns, unique=False):
        if not _idx_exists(table, index_name):
            op.create_index(index_name, table, columns, unique=unique)

    def _drop_index_if_exists(index_name, table):
        if _idx_exists(table, index_name):
            op.drop_index(index_name, table_name=table)

    def _drop_fk_if_exists(table, fk_name):
        if _fk_exists(table, fk_name):
            conn.execute(sa.text(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}"))

    def _create_fk_if_not_exists(table, fk_name, col, ref_table, ref_col):
        if not _fk_exists(table, fk_name):
            conn.execute(sa.text(
                f"ALTER TABLE {table} ADD CONSTRAINT {fk_name} "
                f"FOREIGN KEY ({col}) REFERENCES {ref_table} ({ref_col})"
            ))

    # === STEP 1: DROP ALL FK CONSTRAINTS ===
    # Drop spaced_repetition_state / flashcards FKs
    _drop_fk_if_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_2')
    _drop_fk_if_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_1')
    _drop_fk_if_exists('flashcards', 'flashcards_ibfk_2')
    _drop_fk_if_exists('flashcards', 'flashcards_ibfk_1')

    # Drop stray or typo FKs
    _drop_fk_if_exists('spaced_reduction_state', 'spaced_reduction_state_ibfk_2')

    # Drop vocabulary incoming FKs to vocabulary_items
    _drop_fk_if_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_1')
    _drop_fk_if_exists('vocabulary_errors', 'vocabulary_errors_ibfk_2')
    _drop_fk_if_exists('vocabulary_examples', 'vocabulary_examples_ibfk_1')
    _drop_fk_if_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_3')
    _drop_fk_if_exists('vocabulary_relations', 'vocabulary_relations_ibfk_2')
    _drop_fk_if_exists('vocabulary_relations', 'vocabulary_relations_ibfk_3')

    # Drop vocabulary incoming FKs to vocabulary_topics
    _drop_fk_if_exists('vocabulary_topics', 'vocabulary_topics_ibfk_2')
    _drop_fk_if_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_2')

    # Drop vocabulary incoming FKs to vocabulary_nodes
    _drop_fk_if_exists('vocabulary_edges', 'vocabulary_edges_ibfk_2')
    _drop_fk_if_exists('vocabulary_edges', 'vocabulary_edges_ibfk_3')

    # Drop player_id FKs on all vocabulary tables
    _drop_fk_if_exists('vocabulary_items', 'vocabulary_items_ibfk_1')
    _drop_fk_if_exists('vocabulary_topics', 'vocabulary_topics_ibfk_1')
    _drop_fk_if_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_1')
    _drop_fk_if_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_2')
    _drop_fk_if_exists('vocabulary_edges', 'vocabulary_edges_ibfk_1')
    _drop_fk_if_exists('vocabulary_errors', 'vocabulary_errors_ibfk_1')
    _drop_fk_if_exists('vocabulary_examples', 'vocabulary_examples_ibfk_2')
    _drop_fk_if_exists('vocabulary_relations', 'vocabulary_relations_ibfk_1')

    # === STEP 2: ALTER ALL COLUMNS FROM BIGINT TO INT ===
    # flashcards
    op.alter_column('flashcards', 'id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('flashcards', 'vocabulary_item_id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)

    # spaced_repetition_state
    op.alter_column('spaced_repetition_state', 'id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('spaced_repetition_state', 'flashcard_id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False)

    # player_xp_transactions
    op.alter_column('player_xp_transactions', 'id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)

    # quest_templates completion_payload text type update
    op.alter_column('quest_templates', 'completion_payload',
               existing_type=mysql.TEXT(),
               nullable=False)

    # quests completion_payload text type update
    op.alter_column('quests', 'completion_payload',
               existing_type=mysql.TEXT(),
               nullable=False)

    # skill_xp_transactions
    op.alter_column('skill_xp_transactions', 'id',
               existing_type=mysql.BIGINT(),
               type_=sa.Integer(),
               existing_nullable=False,
               autoincrement=True)

    # vocabulary tables bigint -> int
    conn.execute(sa.text("ALTER TABLE vocabulary_items MODIFY id INT NOT NULL AUTO_INCREMENT"))
    conn.execute(sa.text("ALTER TABLE vocabulary_topics MODIFY id INT NOT NULL AUTO_INCREMENT, MODIFY parent_topic_id INT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_nodes MODIFY id INT NOT NULL AUTO_INCREMENT, MODIFY topic_id INT NOT NULL, MODIFY vocabulary_item_id INT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_collocations MODIFY id INT NOT NULL AUTO_INCREMENT, MODIFY vocabulary_item_id INT NOT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_edges MODIFY id INT NOT NULL AUTO_INCREMENT, MODIFY source_node_id INT NOT NULL, MODIFY target_node_id INT NOT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_errors MODIFY vocabulary_item_id INT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_examples MODIFY id INT NOT NULL AUTO_INCREMENT, MODIFY vocabulary_item_id INT NOT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_relations MODIFY id INT NOT NULL AUTO_INCREMENT, MODIFY source_word_id INT NOT NULL, MODIFY target_word_id INT NULL"))

    # weakness_suggestions
    op.alter_column('weakness_suggestions', 'campaign_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    # === STEP 3: ADD NEW COLUMNS, CONSTRAINTS & CERTIFICATE FKS ===
    # rank_exam_pools xp_threshold column
    if not _col_exists('rank_exam_pools', 'xp_threshold'):
        op.add_column('rank_exam_pools', sa.Column('xp_threshold', sa.Integer(), nullable=False))

    # campaign_skill_states check constraint
    if not _check_exists('campaign_skill_states', 'ck_promotion_status'):
        op.create_check_constraint(
            'ck_promotion_status', 'campaign_skill_states',
            "promotion_status IN ('none','eligible','boss_required','in_progress','passed','failed')"
        )

    # skill_rank_history source_certificate_record_id
    if not _col_exists('skill_rank_history', 'source_certificate_record_id'):
        op.add_column('skill_rank_history', sa.Column('source_certificate_record_id', sa.Integer(), nullable=True))
    _create_index_if_not_exists(
        'ix_skill_rank_history_source_certificate_record_id',
        'skill_rank_history', ['source_certificate_record_id']
    )
    if not _fk_exists('skill_rank_history', 'fk_skill_rank_history_cert_record'):
        op.create_foreign_key(
            'fk_skill_rank_history_cert_record',
            'skill_rank_history', 'certificate_records',
            ['source_certificate_record_id'], ['id']
        )

    # skill_rank_suggestions source_certificate_record_id
    if not _col_exists('skill_rank_suggestions', 'source_certificate_record_id'):
        op.add_column('skill_rank_suggestions', sa.Column('source_certificate_record_id', sa.Integer(), nullable=True))
    _create_index_if_not_exists(
        'ix_skill_rank_suggestions_source_certificate_record_id',
        'skill_rank_suggestions', ['source_certificate_record_id']
    )
    if not _fk_exists('skill_rank_suggestions', 'fk_skill_rank_suggestions_cert_record'):
        op.create_foreign_key(
            'fk_skill_rank_suggestions_cert_record',
            'skill_rank_suggestions', 'certificate_records',
            ['source_certificate_record_id'], ['id']
        )

    # === STEP 4: CREATE / DROP INDEXES ===
    # player_xp_transactions
    _create_index_if_not_exists('ix_player_xp_transactions_id', 'player_xp_transactions', ['id'])
    _create_index_if_not_exists('ix_player_xp_transactions_idempotency_key', 'player_xp_transactions', ['idempotency_key'])

    # quest_templates
    _create_index_if_not_exists('ix_quest_templates_activity_type', 'quest_templates', ['activity_type'])
    _create_index_if_not_exists('ix_quest_templates_quest_track_code', 'quest_templates', ['quest_track_code'])
    _create_index_if_not_exists('ix_quest_templates_reward_skill_id', 'quest_templates', ['reward_skill_id'])

    # quests
    _create_index_if_not_exists('ix_quests_activity_type', 'quests', ['activity_type'])
    _create_index_if_not_exists('ix_quests_quest_track_code', 'quests', ['quest_track_code'])
    _create_index_if_not_exists('ix_quests_reward_skill_id', 'quests', ['reward_skill_id'])

    # skill_xp_transactions
    _create_index_if_not_exists('ix_skill_xp_transactions_id', 'skill_xp_transactions', ['id'])
    _create_index_if_not_exists('ix_skill_xp_transactions_idempotency_key', 'skill_xp_transactions', ['idempotency_key'])

    # spaced_repetition_state
    _drop_index_if_exists('idx_spaced_repetition_player_id', 'spaced_repetition_state')
    _drop_index_if_exists('idx_spaced_repetition_flashcard_id', 'spaced_repetition_state')
    _create_index_if_not_exists('ix_spaced_repetition_state_flashcard_id', 'spaced_repetition_state', ['flashcard_id'])
    _create_index_if_not_exists('ix_spaced_repetition_state_id', 'spaced_repetition_state', ['id'])
    _create_index_if_not_exists('ix_spaced_repetition_state_player_id', 'spaced_repetition_state', ['player_id'])

    # vocabulary_items
    _drop_index_if_exists('idx_vocabulary_items_player_id', 'vocabulary_items')
    _drop_index_if_exists('idx_vocabulary_items_rank', 'vocabulary_items')
    _drop_index_if_exists('idx_vocabulary_items_topic', 'vocabulary_items')
    _drop_index_if_exists('idx_vocabulary_items_word', 'vocabulary_items')
    _create_index_if_not_exists('ix_vocabulary_items_id', 'vocabulary_items', ['id'])
    _create_index_if_not_exists('ix_vocabulary_items_ielts_topic', 'vocabulary_items', ['ielts_topic'])
    _create_index_if_not_exists('ix_vocabulary_items_mastery_rank', 'vocabulary_items', ['mastery_rank'])
    _create_index_if_not_exists('ix_vocabulary_items_normalized_word', 'vocabulary_items', ['normalized_word'])
    _create_index_if_not_exists('ix_vocabulary_items_player_id', 'vocabulary_items', ['player_id'])
    _create_index_if_not_exists('ix_vocabulary_items_word', 'vocabulary_items', ['word'])

    # vocabulary_topics
    _drop_index_if_exists('idx_vocabulary_topics_parent_id', 'vocabulary_topics')
    _drop_index_if_exists('idx_vocabulary_topics_player_id', 'vocabulary_topics')
    _create_index_if_not_exists('ix_vocabulary_topics_id', 'vocabulary_topics', ['id'])
    _create_index_if_not_exists('ix_vocabulary_topics_parent_topic_id', 'vocabulary_topics', ['parent_topic_id'])
    _create_index_if_not_exists('ix_vocabulary_topics_player_id', 'vocabulary_topics', ['player_id'])

    # vocabulary_nodes
    _drop_index_if_exists('idx_vocabulary_nodes_item_id', 'vocabulary_nodes')
    _drop_index_if_exists('idx_vocabulary_nodes_player_id', 'vocabulary_nodes')
    _drop_index_if_exists('idx_vocabulary_nodes_topic_id', 'vocabulary_nodes')
    _create_index_if_not_exists('ix_vocabulary_nodes_id', 'vocabulary_nodes', ['id'])
    _create_index_if_not_exists('ix_vocabulary_nodes_player_id', 'vocabulary_nodes', ['player_id'])
    _create_index_if_not_exists('ix_vocabulary_nodes_topic_id', 'vocabulary_nodes', ['topic_id'])
    _create_index_if_not_exists('ix_vocabulary_nodes_vocabulary_item_id', 'vocabulary_nodes', ['vocabulary_item_id'])

    # vocabulary_collocations
    _drop_index_if_exists('idx_vocabulary_collocations_item_id', 'vocabulary_collocations')
    _drop_index_if_exists('idx_vocabulary_collocations_player_id', 'vocabulary_collocations')
    _create_index_if_not_exists('ix_vocabulary_collocations_id', 'vocabulary_collocations', ['id'])
    _create_index_if_not_exists('ix_vocabulary_collocations_player_id', 'vocabulary_collocations', ['player_id'])
    _create_index_if_not_exists('ix_vocabulary_collocations_vocabulary_item_id', 'vocabulary_collocations', ['vocabulary_item_id'])

    # vocabulary_edges
    _drop_index_if_exists('idx_vocabulary_edges_player_id', 'vocabulary_edges')
    _drop_index_if_exists('idx_vocabulary_edges_source_id', 'vocabulary_edges')
    _drop_index_if_exists('idx_vocabulary_edges_target_id', 'vocabulary_edges')
    _create_index_if_not_exists('ix_vocabulary_edges_id', 'vocabulary_edges', ['id'])
    _create_index_if_not_exists('ix_vocabulary_edges_player_id', 'vocabulary_edges', ['player_id'])
    _create_index_if_not_exists('ix_vocabulary_edges_source_node_id', 'vocabulary_edges', ['source_node_id'])
    _create_index_if_not_exists('ix_vocabulary_edges_target_node_id', 'vocabulary_edges', ['target_node_id'])

    # vocabulary_examples
    _drop_index_if_exists('idx_vocabulary_examples_item_id', 'vocabulary_examples')
    _drop_index_if_exists('idx_vocabulary_examples_player_id', 'vocabulary_examples')
    _create_index_if_not_exists('ix_vocabulary_examples_id', 'vocabulary_examples', ['id'])
    _create_index_if_not_exists('ix_vocabulary_examples_player_id', 'vocabulary_examples', ['player_id'])
    _create_index_if_not_exists('ix_vocabulary_examples_vocabulary_item_id', 'vocabulary_examples', ['vocabulary_item_id'])

    # vocabulary_relations
    _drop_index_if_exists('idx_vocabulary_relations_player_id', 'vocabulary_relations')
    _drop_index_if_exists('idx_vocabulary_relations_source_id', 'vocabulary_relations')
    _drop_index_if_exists('idx_vocabulary_relations_target_id', 'vocabulary_relations')
    _create_index_if_not_exists('ix_vocabulary_relations_id', 'vocabulary_relations', ['id'])
    _create_index_if_not_exists('ix_vocabulary_relations_player_id', 'vocabulary_relations', ['player_id'])
    _create_index_if_not_exists('ix_vocabulary_relations_source_word_id', 'vocabulary_relations', ['source_word_id'])
    _create_index_if_not_exists('ix_vocabulary_relations_target_word_id', 'vocabulary_relations', ['target_word_id'])

    # weekly_missions
    _create_index_if_not_exists('ix_weekly_missions_activity_type', 'weekly_missions', ['activity_type'])
    _create_index_if_not_exists('ix_weekly_missions_mission_track_code', 'weekly_missions', ['mission_track_code'])
    _create_index_if_not_exists('ix_weekly_missions_primary_skill_id', 'weekly_missions', ['primary_skill_id'])
    _create_index_if_not_exists('ix_weekly_missions_reward_skill_id', 'weekly_missions', ['reward_skill_id'])

    # === STEP 5: RECREATE ALL FK CONSTRAINTS ===
    # flashcards / spaced_repetition_state
    _create_fk_if_not_exists('flashcards', 'flashcards_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('flashcards', 'flashcards_ibfk_2', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_2', 'flashcard_id', 'flashcards', 'id')

    # vocabulary FKs referencing vocabulary_items.id
    _create_fk_if_not_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_1', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_errors', 'vocabulary_errors_ibfk_2', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_examples', 'vocabulary_examples_ibfk_1', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_3', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_relations', 'vocabulary_relations_ibfk_2', 'source_word_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_relations', 'vocabulary_relations_ibfk_3', 'target_word_id', 'vocabulary_items', 'id')

    # vocabulary FKs referencing vocabulary_topics.id
    _create_fk_if_not_exists('vocabulary_topics', 'vocabulary_topics_ibfk_2', 'parent_topic_id', 'vocabulary_topics', 'id')
    _create_fk_if_not_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_2', 'topic_id', 'vocabulary_topics', 'id')

    # vocabulary FKs referencing vocabulary_nodes.id
    _create_fk_if_not_exists('vocabulary_edges', 'vocabulary_edges_ibfk_2', 'source_node_id', 'vocabulary_nodes', 'id')
    _create_fk_if_not_exists('vocabulary_edges', 'vocabulary_edges_ibfk_3', 'target_node_id', 'vocabulary_nodes', 'id')

    # player_id FKs on all vocabulary tables
    _create_fk_if_not_exists('vocabulary_items', 'vocabulary_items_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_topics', 'vocabulary_topics_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_2', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_edges', 'vocabulary_edges_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_errors', 'vocabulary_errors_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_examples', 'vocabulary_examples_ibfk_2', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_relations', 'vocabulary_relations_ibfk_1', 'player_id', 'players', 'id')


def downgrade() -> None:
    conn = op.get_bind()

    # Helpers for idempotent checks
    def _idx_exists(table, index_name):
        r = conn.execute(sa.text(
            "SELECT INDEX_NAME FROM information_schema.STATISTICS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND INDEX_NAME=:i LIMIT 1"
        ), {"t": table, "i": index_name})
        return r.fetchone() is not None

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

    def _check_exists(table, constraint_name):
        r = conn.execute(sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS "
            "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND CONSTRAINT_NAME=:c AND CONSTRAINT_TYPE='CHECK' LIMIT 1"
        ), {"t": table, "c": constraint_name})
        return r.fetchone() is not None

    def _create_index_if_not_exists(index_name, table, columns, unique=False):
        if not _idx_exists(table, index_name):
            op.create_index(index_name, table, columns, unique=unique)

    def _drop_index_if_exists(index_name, table):
        if _idx_exists(table, index_name):
            op.drop_index(index_name, table_name=table)

    def _drop_fk_if_exists(table, fk_name):
        if _fk_exists(table, fk_name):
            conn.execute(sa.text(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}"))

    def _create_fk_if_not_exists(table, fk_name, col, ref_table, ref_col):
        if not _fk_exists(table, fk_name):
            conn.execute(sa.text(
                f"ALTER TABLE {table} ADD CONSTRAINT {fk_name} "
                f"FOREIGN KEY ({col}) REFERENCES {ref_table} ({ref_col})"
            ))

    # === STEP 1: DROP ALL FK CONSTRAINTS ===
    # Drop spaced_repetition_state / flashcards FKs
    _drop_fk_if_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_2')
    _drop_fk_if_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_1')
    _drop_fk_if_exists('flashcards', 'flashcards_ibfk_2')
    _drop_fk_if_exists('flashcards', 'flashcards_ibfk_1')

    # Drop vocabulary incoming FKs to vocabulary_items
    _drop_fk_if_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_1')
    _drop_fk_if_exists('vocabulary_errors', 'vocabulary_errors_ibfk_2')
    _drop_fk_if_exists('vocabulary_examples', 'vocabulary_examples_ibfk_1')
    _drop_fk_if_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_3')
    _drop_fk_if_exists('vocabulary_relations', 'vocabulary_relations_ibfk_2')
    _drop_fk_if_exists('vocabulary_relations', 'vocabulary_relations_ibfk_3')

    # Drop vocabulary incoming FKs to vocabulary_topics
    _drop_fk_if_exists('vocabulary_topics', 'vocabulary_topics_ibfk_2')
    _drop_fk_if_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_2')

    # Drop vocabulary incoming FKs to vocabulary_nodes
    _drop_fk_if_exists('vocabulary_edges', 'vocabulary_edges_ibfk_2')
    _drop_fk_if_exists('vocabulary_edges', 'vocabulary_edges_ibfk_3')

    # Drop player_id FKs on all vocabulary tables
    _drop_fk_if_exists('vocabulary_items', 'vocabulary_items_ibfk_1')
    _drop_fk_if_exists('vocabulary_topics', 'vocabulary_topics_ibfk_1')
    _drop_fk_if_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_1')
    _drop_fk_if_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_2')
    _drop_fk_if_exists('vocabulary_edges', 'vocabulary_edges_ibfk_1')
    _drop_fk_if_exists('vocabulary_errors', 'vocabulary_errors_ibfk_1')
    _drop_fk_if_exists('vocabulary_examples', 'vocabulary_examples_ibfk_2')
    _drop_fk_if_exists('vocabulary_relations', 'vocabulary_relations_ibfk_1')

    # === STEP 2: ALTER ALL COLUMNS BACK TO BIGINT ===
    # flashcards
    op.alter_column('flashcards', 'id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('flashcards', 'vocabulary_item_id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False)

    # spaced_repetition_state
    op.alter_column('spaced_repetition_state', 'id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('spaced_repetition_state', 'flashcard_id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False)

    # player_xp_transactions
    op.alter_column('player_xp_transactions', 'id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False,
               autoincrement=True)

    # quest_templates completion_payload
    op.alter_column('quest_templates', 'completion_payload',
               existing_type=mysql.TEXT(),
               nullable=True)

    # quests completion_payload
    op.alter_column('quests', 'completion_payload',
               existing_type=mysql.TEXT(),
               nullable=True)

    # skill_xp_transactions
    op.alter_column('skill_xp_transactions', 'id',
               existing_type=sa.Integer(),
               type_=mysql.BIGINT(),
               existing_nullable=False,
               autoincrement=True)

    # vocabulary tables int -> bigint
    conn.execute(sa.text("ALTER TABLE vocabulary_items MODIFY id BIGINT NOT NULL AUTO_INCREMENT"))
    conn.execute(sa.text("ALTER TABLE vocabulary_topics MODIFY id BIGINT NOT NULL AUTO_INCREMENT, MODIFY parent_topic_id BIGINT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_nodes MODIFY id BIGINT NOT NULL AUTO_INCREMENT, MODIFY topic_id BIGINT NOT NULL, MODIFY vocabulary_item_id BIGINT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_collocations MODIFY id BIGINT NOT NULL AUTO_INCREMENT, MODIFY vocabulary_item_id BIGINT NOT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_edges MODIFY id BIGINT NOT NULL AUTO_INCREMENT, MODIFY source_node_id BIGINT NOT NULL, MODIFY target_node_id BIGINT NOT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_errors MODIFY vocabulary_item_id BIGINT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_examples MODIFY id BIGINT NOT NULL AUTO_INCREMENT, MODIFY vocabulary_item_id BIGINT NOT NULL"))
    conn.execute(sa.text("ALTER TABLE vocabulary_relations MODIFY id BIGINT NOT NULL AUTO_INCREMENT, MODIFY source_word_id BIGINT NOT NULL, MODIFY target_word_id BIGINT NULL"))

    # weakness_suggestions
    op.alter_column('weakness_suggestions', 'campaign_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    # === STEP 3: REMOVE NEW COLUMNS, CONSTRAINTS & CERTIFICATE FKS ===
    # Drop check constraint
    if _check_exists('campaign_skill_states', 'ck_promotion_status'):
        op.drop_constraint('ck_promotion_status', 'campaign_skill_states', type_='check')

    # Drop skill_rank_suggestions columns and FK
    _drop_fk_if_exists('skill_rank_suggestions', 'fk_skill_rank_suggestions_cert_record')
    _drop_index_if_exists('ix_skill_rank_suggestions_source_certificate_record_id', 'skill_rank_suggestions')
    if _col_exists('skill_rank_suggestions', 'source_certificate_record_id'):
        op.drop_column('skill_rank_suggestions', 'source_certificate_record_id')

    # Drop skill_rank_history columns and FK
    _drop_fk_if_exists('skill_rank_history', 'fk_skill_rank_history_cert_record')
    _drop_index_if_exists('ix_skill_rank_history_source_certificate_record_id', 'skill_rank_history')
    if _col_exists('skill_rank_history', 'source_certificate_record_id'):
        op.drop_column('skill_rank_history', 'source_certificate_record_id')

    # Drop rank_exam_pools columns
    if _col_exists('rank_exam_pools', 'xp_threshold'):
        op.drop_column('rank_exam_pools', 'xp_threshold')

    # === STEP 4: REVERT / RECREATE INDEXES ===
    # player_xp_transactions
    _drop_index_if_exists('ix_player_xp_transactions_id', 'player_xp_transactions')
    _drop_index_if_exists('ix_player_xp_transactions_idempotency_key', 'player_xp_transactions')

    # quest_templates
    _drop_index_if_exists('ix_quest_templates_activity_type', 'quest_templates')
    _drop_index_if_exists('ix_quest_templates_quest_track_code', 'quest_templates')
    _drop_index_if_exists('ix_quest_templates_reward_skill_id', 'quest_templates')

    # quests
    _drop_index_if_exists('ix_quests_activity_type', 'quests')
    _drop_index_if_exists('ix_quests_quest_track_code', 'quests')
    _drop_index_if_exists('ix_quests_reward_skill_id', 'quests')

    # skill_xp_transactions
    _drop_index_if_exists('ix_skill_xp_transactions_id', 'skill_xp_transactions')
    _drop_index_if_exists('ix_skill_xp_transactions_idempotency_key', 'skill_xp_transactions')

    # spaced_repetition_state
    _drop_index_if_exists('ix_spaced_repetition_state_flashcard_id', 'spaced_repetition_state')
    _drop_index_if_exists('ix_spaced_repetition_state_id', 'spaced_repetition_state')
    _drop_index_if_exists('ix_spaced_repetition_state_player_id', 'spaced_repetition_state')
    _create_index_if_not_exists('idx_spaced_repetition_player_id', 'spaced_repetition_state', ['player_id'])
    _create_index_if_not_exists('idx_spaced_repetition_flashcard_id', 'spaced_repetition_state', ['flashcard_id'])

    # vocabulary_items
    _drop_index_if_exists('ix_vocabulary_items_id', 'vocabulary_items')
    _drop_index_if_exists('ix_vocabulary_items_ielts_topic', 'vocabulary_items')
    _drop_index_if_exists('ix_vocabulary_items_mastery_rank', 'vocabulary_items')
    _drop_index_if_exists('ix_vocabulary_items_normalized_word', 'vocabulary_items')
    _drop_index_if_exists('ix_vocabulary_items_player_id', 'vocabulary_items')
    _drop_index_if_exists('ix_vocabulary_items_word', 'vocabulary_items')
    _create_index_if_not_exists('idx_vocabulary_items_player_id', 'vocabulary_items', ['player_id'])
    _create_index_if_not_exists('idx_vocabulary_items_rank', 'vocabulary_items', ['mastery_rank'])
    _create_index_if_not_exists('idx_vocabulary_items_topic', 'vocabulary_items', ['ielts_topic'])
    _create_index_if_not_exists('idx_vocabulary_items_word', 'vocabulary_items', ['normalized_word'])

    # vocabulary_topics
    _drop_index_if_exists('ix_vocabulary_topics_id', 'vocabulary_topics')
    _drop_index_if_exists('ix_vocabulary_topics_parent_topic_id', 'vocabulary_topics')
    _drop_index_if_exists('ix_vocabulary_topics_player_id', 'vocabulary_topics')
    _create_index_if_not_exists('idx_vocabulary_topics_parent_id', 'vocabulary_topics', ['parent_topic_id'])
    _create_index_if_not_exists('idx_vocabulary_topics_player_id', 'vocabulary_topics', ['player_id'])

    # vocabulary_nodes
    _drop_index_if_exists('ix_vocabulary_nodes_id', 'vocabulary_nodes')
    _drop_index_if_exists('ix_vocabulary_nodes_player_id', 'vocabulary_nodes')
    _drop_index_if_exists('ix_vocabulary_nodes_topic_id', 'vocabulary_nodes')
    _drop_index_if_exists('ix_vocabulary_nodes_vocabulary_item_id', 'vocabulary_nodes')
    _create_index_if_not_exists('idx_vocabulary_nodes_item_id', 'vocabulary_nodes', ['vocabulary_item_id'])
    _create_index_if_not_exists('idx_vocabulary_nodes_player_id', 'vocabulary_nodes', ['player_id'])
    _create_index_if_not_exists('idx_vocabulary_nodes_topic_id', 'vocabulary_nodes', ['topic_id'])

    # vocabulary_collocations
    _drop_index_if_exists('ix_vocabulary_collocations_id', 'vocabulary_collocations')
    _drop_index_if_exists('ix_vocabulary_collocations_player_id', 'vocabulary_collocations')
    _drop_index_if_exists('ix_vocabulary_collocations_vocabulary_item_id', 'vocabulary_collocations')
    _create_index_if_not_exists('idx_vocabulary_collocations_item_id', 'vocabulary_collocations', ['vocabulary_item_id'])
    _create_index_if_not_exists('idx_vocabulary_collocations_player_id', 'vocabulary_collocations', ['player_id'])

    # vocabulary_edges
    _drop_index_if_exists('ix_vocabulary_edges_id', 'vocabulary_edges')
    _drop_index_if_exists('ix_vocabulary_edges_player_id', 'vocabulary_edges')
    _drop_index_if_exists('ix_vocabulary_edges_source_node_id', 'vocabulary_edges')
    _drop_index_if_exists('ix_vocabulary_edges_target_node_id', 'vocabulary_edges')
    _create_index_if_not_exists('idx_vocabulary_edges_player_id', 'vocabulary_edges', ['player_id'])
    _create_index_if_not_exists('idx_vocabulary_edges_source_id', 'vocabulary_edges', ['source_node_id'])
    _create_index_if_not_exists('idx_vocabulary_edges_target_id', 'vocabulary_edges', ['target_node_id'])

    # vocabulary_examples
    _drop_index_if_exists('ix_vocabulary_examples_id', 'vocabulary_examples')
    _drop_index_if_exists('ix_vocabulary_examples_player_id', 'vocabulary_examples')
    _drop_index_if_exists('ix_vocabulary_examples_vocabulary_item_id', 'vocabulary_examples')
    _create_index_if_not_exists('idx_vocabulary_examples_item_id', 'vocabulary_examples', ['vocabulary_item_id'])
    _create_index_if_not_exists('idx_vocabulary_examples_player_id', 'vocabulary_examples', ['player_id'])

    # vocabulary_relations
    _drop_index_if_exists('ix_vocabulary_relations_id', 'vocabulary_relations')
    _drop_index_if_exists('ix_vocabulary_relations_player_id', 'vocabulary_relations')
    _drop_index_if_exists('ix_vocabulary_relations_source_word_id', 'vocabulary_relations')
    _drop_index_if_exists('ix_vocabulary_relations_target_word_id', 'vocabulary_relations')
    _create_index_if_not_exists('idx_vocabulary_relations_id', 'vocabulary_relations', ['id'])
    _create_index_if_not_exists('idx_vocabulary_relations_player_id', 'vocabulary_relations', ['player_id'])
    _create_index_if_not_exists('idx_vocabulary_relations_source_id', 'vocabulary_relations', ['source_word_id'])
    _create_index_if_not_exists('idx_vocabulary_relations_target_id', 'vocabulary_relations', ['target_word_id'])

    # weekly_missions
    _drop_index_if_exists('ix_weekly_missions_activity_type', 'weekly_missions')
    _drop_index_if_exists('ix_weekly_missions_mission_track_code', 'weekly_missions')
    _drop_index_if_exists('ix_weekly_missions_primary_skill_id', 'weekly_missions')
    _drop_index_if_exists('ix_weekly_missions_reward_skill_id', 'weekly_missions')

    # flashcards
    _drop_index_if_exists('ix_flashcards_id', 'flashcards')
    _drop_index_if_exists('ix_flashcards_player_id', 'flashcards')
    _drop_index_if_exists('ix_flashcards_vocabulary_item_id', 'flashcards')
    _create_index_if_not_exists('idx_flashcards_player_id', 'flashcards', ['player_id'])
    _create_index_if_not_exists('idx_flashcards_item_id', 'flashcards', ['vocabulary_item_id'])

    # === STEP 5: RECREATE ORIGINAL FK CONSTRAINTS ===
    # flashcards / spaced_repetition_state
    _create_fk_if_not_exists('flashcards', 'flashcards_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('flashcards', 'flashcards_ibfk_2', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('spaced_repetition_state', 'spaced_repetition_state_ibfk_2', 'flashcard_id', 'flashcards', 'id')

    # vocabulary FKs referencing vocabulary_items.id
    _create_fk_if_not_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_1', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_errors', 'vocabulary_errors_ibfk_2', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_examples', 'vocabulary_examples_ibfk_1', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_3', 'vocabulary_item_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_relations', 'vocabulary_relations_ibfk_2', 'source_word_id', 'vocabulary_items', 'id')
    _create_fk_if_not_exists('vocabulary_relations', 'vocabulary_relations_ibfk_3', 'target_word_id', 'vocabulary_items', 'id')

    # vocabulary FKs referencing vocabulary_topics.id
    _create_fk_if_not_exists('vocabulary_topics', 'vocabulary_topics_ibfk_2', 'parent_topic_id', 'vocabulary_topics', 'id')
    _create_fk_if_not_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_2', 'topic_id', 'vocabulary_topics', 'id')

    # vocabulary FKs referencing vocabulary_nodes.id
    _create_fk_if_not_exists('vocabulary_edges', 'vocabulary_edges_ibfk_2', 'source_node_id', 'vocabulary_nodes', 'id')
    _create_fk_if_not_exists('vocabulary_edges', 'vocabulary_edges_ibfk_3', 'target_node_id', 'vocabulary_nodes', 'id')

    # player_id FKs on all vocabulary tables
    _create_fk_if_not_exists('vocabulary_items', 'vocabulary_items_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_topics', 'vocabulary_topics_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_nodes', 'vocabulary_nodes_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_collocations', 'vocabulary_collocations_ibfk_2', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_edges', 'vocabulary_edges_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_errors', 'vocabulary_errors_ibfk_1', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_examples', 'vocabulary_examples_ibfk_2', 'player_id', 'players', 'id')
    _create_fk_if_not_exists('vocabulary_relations', 'vocabulary_relations_ibfk_1', 'player_id', 'players', 'id')
