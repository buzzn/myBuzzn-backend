from util.database import db


class Group(db.Model):
    """ Represents an energy group in the backend.
    """

    @staticmethod
    def NAME_MAX_LENGTH():
        return Group._name.property.columns[0].type.length

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    group_meter_id = db.Column(db.String(32), unique=True)

    def __init__(self, name, group_meter_id):
        """ Creates a new energy group.
        :param str name: the group name
        :param str meter_id: the group's meter id for the common energy
        """

        self.name = name
        self.group_meter_id = group_meter_id
