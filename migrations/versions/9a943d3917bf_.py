""" Add baseline to user table.

Revision ID: 9a943d3917bf
Revises: 15961d085f89
Create Date: 2020-04-09 12:51:20.706190

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a943d3917bf'
down_revision = '15961d085f89'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('base_line')
    op.add_column('user', sa.Column('baseline', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('user', 'baseline')
    op.create_table('base_line',
                    sa.Column('timestamp', sa.DATETIME(), nullable=False),
                    sa.Column('meter_id', sa.VARCHAR(
                        length=32), nullable=False),
                    sa.Column('baseline', sa.INTEGER(), nullable=True),
                    sa.ForeignKeyConstraint(['meter_id'], ['user.meter_id'], ),
                    sa.PrimaryKeyConstraint('timestamp', 'meter_id')
                    )
