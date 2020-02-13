""" Create tables for user and community savings.

Revision ID: bd7b6930e72e
Revises: 30bc1b16af74
Create Date: 2020-02-12 14:53:05.830906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd7b6930e72e'
down_revision = '30bc1b16af74'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_saving',
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.Column('meter_id', sa.String(
                        length=32), nullable=False),
                    sa.Column('saving', sa.Float(), nullable=True),
                    sa.ForeignKeyConstraint(['meter_id'], ['user.meter_id'], ),
                    sa.PrimaryKeyConstraint('timestamp', 'meter_id')
                    )
    op.create_table('community_saving',
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.Column('saving', sa.Float(), nullable=True),
                    sa.PrimaryKeyConstraint('timestamp')
                    )


def downgrade():
    op.drop_table('user_saving')
    op.drop_table('community_saving')
