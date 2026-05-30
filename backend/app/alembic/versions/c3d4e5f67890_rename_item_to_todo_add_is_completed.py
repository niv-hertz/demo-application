"""Rename item table to todo and add is_completed column

Revision ID: c3d4e5f67890
Revises: fe56fa70289e
Create Date: 2026-05-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f67890'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('item', 'todo')
    op.drop_constraint('item_owner_id_fkey', 'todo', type_='foreignkey')
    op.create_foreign_key(
        'todo_owner_id_fkey', 'todo', 'user', ['owner_id'], ['id'], ondelete='CASCADE'
    )
    op.add_column(
        'todo',
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade():
    op.drop_column('todo', 'is_completed')
    op.drop_constraint('todo_owner_id_fkey', 'todo', type_='foreignkey')
    op.create_foreign_key(
        'item_owner_id_fkey', 'todo', 'user', ['owner_id'], ['id'], ondelete='CASCADE'
    )
    op.rename_table('todo', 'item')
