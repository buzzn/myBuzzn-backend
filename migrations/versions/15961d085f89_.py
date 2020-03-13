""" Alter table group to add production meter ids

Revision ID: 15961d085f89
Revises: 935eefeeaffc
Create Date: 2020-03-13 12:34:00.635039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15961d085f89'
down_revision = '935eefeeaffc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('group', sa.Column(
        'group_production_meter_id_first', sa.String(length=32), nullable=True))
    op.add_column('group', sa.Column(
        'group_production_meter_id_second', sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column('group', 'group_production_meter_id_second')
    op.drop_column('group', 'group_production_meter_id_first')
