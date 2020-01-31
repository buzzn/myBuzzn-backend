""" Create load profile.

Revision ID: 3524888ff528
Revises: ac1e90b27097
Create Date: 2020-01-27 11:24:34.250906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3524888ff528'
down_revision = 'ac1e90b27097'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('loadprofile',
                    sa.Column('date', sa.String(length=33), nullable=False),
                    sa.Column('time', sa.String(length=33), nullable=False),
                    sa.Column('energy', sa.Float(), nullable=True),
                    sa.PrimaryKeyConstraint('date', 'time')
                    )
