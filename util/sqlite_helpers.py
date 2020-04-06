from models.group import Group
from models.user import User


def get_all_meter_ids(session):
    """ Get all meter ids from the SQLite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]\
        + [group_meter_id[0]
           for group_meter_id in session.query(Group.group_meter_id).all()]\
        + [group_production_meter_id_first[0] for
           group_production_meter_id_first in
           session.query(Group.group_production_meter_id_first).all()]\
        + [group_production_meter_id_second[0] for group_production_meter_id_second
           in session.query(Group.group_production_meter_id_second).all()]


def get_all_users(session):
    """ Get all users from the SQLite database. """

    return session.query(User).all()
