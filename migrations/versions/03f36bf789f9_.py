""" Creates a user object.

Revision ID: 03f36bf789f9
Revises: 
Create Date: 2019-12-10 10:33:04.427219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03f36bf789f9'
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
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gender', sa.Enum('FEMALE', 'MALE', 'UNKNOWN', name='gendertype'), nullable=True),
    sa.Column('name', sa.String(length=33), nullable=True),
    sa.Column('mail', sa.String(length=33), nullable=True),
    sa.Column('activation_token', sa.String(length=33), nullable=True),
    sa.Column('password', sa.String(length=333), nullable=True),
    sa.Column('state', sa.Enum('ACTIVATION_PENDING', 'PASSWORT_RESET_PENDING', 'ACTIVE', 'DEACTIVATED', name='statetype'), nullable=True),
    sa.Column('role', sa.Enum('LOCAL_POWER_TAKER', 'ADMINISTRATOR', name='roletype'), nullable=True),
    sa.Column('meter_id', sa.String(length=32), nullable=True),
    sa.Column('inhabitants', sa.Integer(), nullable=True),
    sa.Column('flat_size', sa.Float(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('password_reset_token', sa.String(length=33), nullable=True),
    sa.Column('password_reset_token_expires', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group._id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('activation_token'),
    sa.UniqueConstraint('mail'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('password_reset_token')
    )
    # ### end Alembic commands ###


def downgrade():
    # Delete tables 'group' and 'user'
    op.drop_table('user')
    op.drop_table('group')
    # ### end Alembic commands ###
