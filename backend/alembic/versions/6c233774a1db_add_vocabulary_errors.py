"""add_vocabulary_errors

Revision ID: 6c233774a1db
Revises: 20260607_10
Create Date: 2026-06-06 18:22:57.521213
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c233774a1db'
down_revision = '20260607_10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create vocabulary_errors table
    if 'vocabulary_errors' not in inspector.get_table_names():
        op.create_table('vocabulary_errors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('vocabulary_item_id', sa.BigInteger(), nullable=True),
        sa.Column('error_type', sa.String(length=100), nullable=True),
        sa.Column('wrong_text', sa.Text(), nullable=True),
        sa.Column('corrected_text', sa.Text(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('defeated_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['vocabulary_item_id'], ['vocabulary_items.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_vocabulary_errors_id'), 'vocabulary_errors', ['id'], unique=False)
        op.create_index(op.f('ix_vocabulary_errors_player_id'), 'vocabulary_errors', ['player_id'], unique=False)
        op.create_index(op.f('ix_vocabulary_errors_vocabulary_item_id'), 'vocabulary_errors', ['vocabulary_item_id'], unique=False)

    # Add example_meaning to vocabulary_examples and vocabulary_collocations
    if 'example_meaning' not in [c['name'] for c in inspector.get_columns('vocabulary_examples')]:
        op.add_column('vocabulary_examples', sa.Column('example_meaning', sa.Text(), nullable=True))
    if 'example_meaning' not in [c['name'] for c in inspector.get_columns('vocabulary_collocations')]:
        op.add_column('vocabulary_collocations', sa.Column('example_meaning', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('vocabulary_collocations', 'example_meaning')
    op.drop_column('vocabulary_examples', 'example_meaning')
    op.drop_index(op.f('ix_vocabulary_errors_vocabulary_item_id'), table_name='vocabulary_errors')
    op.drop_index(op.f('ix_vocabulary_errors_player_id'), table_name='vocabulary_errors')
    op.drop_index(op.f('ix_vocabulary_errors_id'), table_name='vocabulary_errors')
    op.drop_table('vocabulary_errors')
