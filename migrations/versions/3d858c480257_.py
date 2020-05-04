""" Add baseline state to user table.

Revision ID: 3d858c480257
Revises: 9a943d3917bf
Create Date: 2020-04-30 14:56:15.623037

"""
from alembic import op
import sqlalchemy as sa

from datetime import datetime

# revision identifiers, used by Alembic.
revision = '3d858c480257'
down_revision = '9a943d3917bf'
branch_labels = None
depends_on = None


def upgrade():

    op.create_table('user_new',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('gender', sa.Enum('FEMALE', 'MALE',
                                                name='gendertype'), nullable=True),
                    sa.Column('name', sa.String(length=33), nullable=True),
                    sa.Column('mail', sa.String(length=33), nullable=True),
                    sa.Column('activation_token', sa.String(
                        length=33), nullable=True),
                    sa.Column('password', sa.String(
                        length=333), nullable=True),
                    sa.Column('state', sa.Enum('ACTIVATION_PENDING', 'PASSWORT_RESET_PENDING',
                                               'ACTIVE', 'DEACTIVATED',
                                               name='statetype'), nullable=True),
                    sa.Column('role', sa.Enum('LOCAL_POWER_TAKER',
                                              'ADMINISTRATOR', name='roletype'), nullable=True),
                    sa.Column('meter_id', sa.String(length=32), nullable=True),
                    sa.Column('inhabitants', sa.Integer(), nullable=True),
                    sa.Column('flat_size', sa.Float(), nullable=True),
                    sa.Column('group_id', sa.Integer(), nullable=True),
                    sa.Column('password_reset_token', sa.String(
                        length=33), nullable=True),
                    sa.Column('password_reset_token_expires',
                              sa.DateTime(), nullable=True),
                    sa.Column('nick', sa.String(length=33), nullable=True),
                    sa.Column('first_name', sa.String(length=33), nullable=True),
                    sa.Column('avatar', sa.LargeBinary(), nullable=True),
                    sa.Column('registration_date', sa.DateTime(), nullable=True),
                    sa.Column('baseline', sa.Integer(), nullable=True),
                    sa.Column('baseline_state', sa.Enum('WAITING_FOR_DATA',
                                                        'NO_READINGS_AVAILABLE',
                                                        'READY',
                                                        name='baselinestatetype'), nullable=True),
                    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('activation_token'),
                    sa.UniqueConstraint('name'),
                    sa.UniqueConstraint('password_reset_token')
                    )

    user_table = sa.sql.table('user_new',
                              sa.Column('id', sa.Integer(), nullable=False),
                              sa.Column('gender', sa.Enum('FEMALE', 'MALE',
                                                          name='gendertype'), nullable=True),
                              sa.Column('name', sa.String(length=33), nullable=True),
                              sa.Column('mail', sa.String(length=33), nullable=True),
                              sa.Column('activation_token', sa.String(
                                  length=33), nullable=True),
                              sa.Column('password', sa.String(
                                  length=333), nullable=True),
                              sa.Column('state',
                                        sa.Enum('ACTIVATION_PENDING', 'PASSWORT_RESET_PENDING',
                                                'ACTIVE', 'DEACTIVATED',
                                                name='statetype'), nullable=True),
                              sa.Column('role', sa.Enum('LOCAL_POWER_TAKER',
                                                        'ADMINISTRATOR', name='roletype'),
                                        nullable=True),
                              sa.Column('meter_id', sa.String(length=32), nullable=True),
                              sa.Column('inhabitants', sa.Integer(), nullable=True),
                              sa.Column('flat_size', sa.Float(), nullable=True),
                              sa.Column('group_id', sa.Integer(), nullable=True),
                              sa.Column('password_reset_token', sa.String(
                                  length=33), nullable=True),
                              sa.Column('password_reset_token_expires',
                                        sa.DateTime(), nullable=True),
                              sa.Column('nick', sa.String(length=33), nullable=True),
                              sa.Column('first_name', sa.String(length=33), nullable=True),
                              sa.Column('avatar', sa.LargeBinary(), nullable=True),
                              sa.Column('registration_date', sa.DateTime(), nullable=True),
                              sa.Column('baseline', sa.Integer(), nullable=True),
                              sa.Column('baseline_state', sa.Enum('WAITING_FOR_DATA',
                                                                  'NO_READINGS_AVAILABLE',
                                                                  'READY',
                                                                  name='baselinestatetype'),
                                        nullable=True))
    conn = op.get_bind()
    res = conn.execute("select * from user")
    results = res.fetchall()

    # get the db engine and reflect database tables
    user_old = []
    for user_entry in results:
        user_entry_dict ={'id': user_entry.id,
                          'gender': user_entry.gender,
                          'first_name': user_entry.first_name,
                          'name': user_entry.name,
                          'nick': user_entry.nick,
                          'mail': user_entry.mail,
                          'activation_token': user_entry.activation_token,
                          'password': user_entry.password,
                          'state': user_entry.state,
                          'role': user_entry.role,
                          'meter_id': user_entry.meter_id,
                          'inhabitants': user_entry.inhabitants,
                          'flat_size': user_entry.flat_size,
                          'group_id': user_entry.group_id,
                          'password_reset_token': user_entry.password_reset_token,
                          'avatar': user_entry.avatar,
                          'baseline': user_entry.baseline,
                          'baseline_state': 'WAITING_FOR_DATA'}

        if user_entry.password_reset_token_expires:
            user_entry_dict['password_reset_token_expires'] = datetime.strptime(
                user_entry.password_reset_token_expires, "%Y-%m-%d %H:%M:%S.%f")
        else:
            user_entry_dict['password_reset_token_expires'] = datetime.strptime(
                "2000-01-01 00:00:00.000000", "%Y-%m-%d %H:%M:%S.%f")

        if user_entry.registration_date:
            user_entry_dict['registration_date'] = datetime.strptime(user_entry.registration_date,
                                                                     "%Y-%m-%d %H:%M:%S.%f")
        user_old.append(user_entry_dict)

    op.bulk_insert(user_table, user_old)
    op.drop_table('user')
    op.rename_table('user_new', 'user')

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'baseline_state')
    # ### end Alembic commands ###
