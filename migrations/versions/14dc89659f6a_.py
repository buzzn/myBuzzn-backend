""" Remove foreign key user_id from table user_savings

Revision ID: 14dc89659f6a
Revises: bd7b6930e72e
Create Date: 2020-02-12 15:49:50.425823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14dc89659f6a'
down_revision = 'bd7b6930e72e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(None, 'user_saving', type_='foreignkey')
    op.drop_column('user_saving', 'id')


def downgrade():
    op.add_column('user_saving', sa.Column('id', sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, 'user_saving', 'user', ['id'], ['id'])
