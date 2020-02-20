""" Create table for baseline values. 

Revision ID: cb69cd66e512
Revises: bd7b6930e72e
Create Date: 2020-02-20 11:05:30.395541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb69cd66e512'
down_revision = 'bd7b6930e72e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('base_line',
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.Column('meter_id', sa.String(
                        length=32), nullable=False),
                    sa.Column('baseline', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['meter_id'], ['user.meter_id'], ),
                    sa.PrimaryKeyConstraint('timestamp', 'meter_id')
                    )


def downgrade():
    op.drop_table('base_line')
