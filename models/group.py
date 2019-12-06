from util.database import db


class Group(db.Model):
    """ Represents an energy group in the backend.
    """

    @staticmethod
    def NAME_MAX_LENGTH():
        return 100

    _id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(100), unique=True)
    _group_meter_id = db.Column(db.String(32), unique=True)

    def __init__(self, name, group_meter_id, members):
        """ Creates a new energy group.
        :param str name: the group name
        :param str meter_id: the group's meter id for the common energy
        :param [str] members: the group's members' ids, i.e. their user ids
        """
        self._name = name
        self._group_meter_id = group_meter_id
        self._members = members

    def get_name(self):
        return self._name

    def get_group_meter_id(self):
        return self._group_meter_id

    def get_members(self):
        return self._members
