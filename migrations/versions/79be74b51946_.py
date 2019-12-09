""" Creates a user object.

Revision ID: 79be74b51946
Revises:
Create Date: 2019-12-06 12:42:12.596317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79be74b51946'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Creates a basic group with unique name and group meter id. 
    op.create_table('group',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('_name', sa.String(length=100), nullable=True),
    sa.Column('_group_meter_id', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('_group_meter_id'),
    sa.UniqueConstraint('_name')
    )
    # Creates a basic user with authentication essentials and role.
    op.create_table('user',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('_name', sa.String(length=33), nullable=True),
    sa.Column('_activation_token', sa.String(length=33), nullable=True),
    sa.Column('_password', sa.String(length=333), nullable=True),
    sa.Column('_status', sa.Enum('ACTIVATION_PENDING', 'ACTIVE', 'DISABLED', name='activetype'), nullable=True),
    sa.Column('_role', sa.Enum('LOCAL_POWER_TAKER', 'ADMINISTRATOR', name='roletype'), nullable=True),
    sa.Column('_meter_id', sa.String(length=32), nullable=True),
    sa.Column('_inhabitants', sa.Integer(), nullable=True),
    sa.Column('_flat_size', sa.Float(), nullable=True),
    sa.Column('_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['_group_id'], ['group._id'], ),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('_activation_token'),
    sa.UniqueConstraint('_name')
    )


def downgrade():
    # Delete tables 'group' and 'user'
    op.drop_table('user')
    op.drop_table('group')
