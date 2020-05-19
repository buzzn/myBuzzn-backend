"""Rename PKV to per_capita_consumption

Revision ID: 67a4de7f7cf1
Revises: 15961d085f89
Create Date: 2020-04-06 10:20:32.370132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67a4de7f7cf1'
down_revision = '15961d085f89'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('PKV') as old_table:
        old_table.alter_column('pkv', new_column_name='per_capita_consumption')
        old_table.alter_column('pkv_cumulated', new_column_name='per_capita_consumption_cumulated')
    op.rename_table('PKV', 'per_capita_consumption')


def downgrade():
    op.rename_table('per_capita_consumption', 'PKV')
    with op.batch_alter_table('PKV') as old_table:
        old_table.alter_column('per_capita_consumption', new_column_name='pkv')
        old_table.alter_column('per_capita_consumption_cumulated', new_column_name='pkv_cumulated')
