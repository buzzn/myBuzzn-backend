"""Creates a user object.

Revision ID: b4218a854a1f
Revises: 
Create Date: 2019-11-29 16:12:42.885760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4218a854a1f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### Creates a basic user with authentication essentials and role. ###
    op.create_table('user',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('_name', sa.String(length=33), nullable=True),
    sa.Column('_activation_token', sa.String(length=33), nullable=True),
    sa.Column('_password', sa.String(length=333), nullable=True),
    sa.Column('_status', sa.Enum('ACTIVATION_PENDING', 'ACTIVE', 'DISABLED', name='activetype'), nullable=True),
    sa.Column('_role', sa.Enum('LOCAL_POWER_TAKER', 'ADMINISTRATOR', name='roletype'), nullable=True),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('_activation_token'),
    sa.UniqueConstraint('_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### Remove the user table ###
    op.drop_table('user')
    # ### end Alembic commands ###
