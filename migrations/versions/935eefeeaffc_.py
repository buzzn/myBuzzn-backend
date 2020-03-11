""" Create table PKV

Revision ID: 935eefeeaffc
Revises: cb69cd66e512
Create Date: 2020-02-27 14:39:23.847282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '935eefeeaffc'
down_revision = 'cb69cd66e512'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('PKV',
                    sa.Column('date', sa.DateTime(), nullable=False),
                    sa.Column('meter_id', sa.String(
                        length=32), nullable=False),
                    sa.Column('consumption', sa.Float(), nullable=True),
                    sa.Column('consumption_cumulated',
                              sa.Float(), nullable=True),
                    sa.Column('inhabitants', sa.Integer(), nullable=True),
                    sa.Column('pkv', sa.Float(), nullable=True),
                    sa.Column('pkv_cumulated', sa.Float(), nullable=True),
                    sa.Column('days', sa.Integer(), nullable=True),
                    sa.Column('moving_average', sa.Float(), nullable=True),
                    sa.Column('moving_average_annualized',
                              sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['inhabitants'], ['user.inhabitants'], ),
                    sa.ForeignKeyConstraint(['meter_id'], ['user.meter_id'], ),
                    sa.PrimaryKeyConstraint('date', 'meter_id')
                    )


def downgrade():
    op.drop_table('PKV')
