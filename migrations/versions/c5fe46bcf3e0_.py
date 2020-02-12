"""empty message

Revision ID: c5fe46bcf3e0
Revises: bd7b6930e72e
Create Date: 2020-02-12 16:16:29.193458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5fe46bcf3e0'
down_revision = 'bd7b6930e72e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_saving',
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('meter_id', sa.String(length=32), nullable=False),
    sa.Column('saving', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['meter_id'], ['user.meter_id'], ),
    sa.PrimaryKeyConstraint('timestamp', 'meter_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_saving')
    # ### end Alembic commands ###
