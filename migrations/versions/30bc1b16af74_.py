""" Update user parameters.

Revision ID: 30bc1b16af74
Revises: 3524888ff528
Create Date: 2020-01-27 11:53:31.037037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30bc1b16af74'
down_revision = '3524888ff528'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('avatar', sa.LargeBinary(), nullable=True))
    op.add_column('user', sa.Column(
        'first_name', sa.String(length=33), nullable=True))
    op.add_column('user', sa.Column(
        'nick', sa.String(length=33), nullable=True))


def downgrade():
    op.drop_column('user', 'nick')
    op.drop_column('user', 'first_name')
    op.drop_column('user', 'avatar')
