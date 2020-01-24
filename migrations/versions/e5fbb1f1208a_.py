"""empty message

Revision ID: e5fbb1f1208a
Revises: ac1e90b27097
Create Date: 2020-01-24 11:36:19.988927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5fbb1f1208a'
down_revision = 'ac1e90b27097'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('load_profile',
    sa.Column('date', sa.String(length=33), nullable=False),
    sa.Column('time', sa.String(length=33), nullable=False),
    sa.Column('energy', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('date', 'time')
    )
    op.add_column('user', sa.Column('avatar', sa.LargeBinary(), nullable=True))
    op.add_column('user', sa.Column('first_name', sa.String(length=33), nullable=True))
    op.add_column('user', sa.Column('nick', sa.String(length=33), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'nick')
    op.drop_column('user', 'first_name')
    op.drop_column('user', 'avatar')
    op.drop_table('load_profile')
    # ### end Alembic commands ###
