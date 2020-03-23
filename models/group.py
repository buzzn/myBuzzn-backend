from util.database import db


class Group(db.Model):
    """ Represents an energy group in the backend.
    """

    @staticmethod
    def NAME_MAX_LENGTH():
        return Group.name.property.columns[0].type.length

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    group_meter_id = db.Column(db.String(32), unique=True)
    group_production_meter_id_first = db.Column(
        db.String(32))
    group_production_meter_id_second = db.Column(
        db.String(32))

    def __init__(self, name, group_meter_id, group_production_meter_id_first,
                 group_production_meter_id_second):
        """ Creates a new energy group.
        :param str name: the group name
        :param str group_meter_id: the group's meter id for the common energy
        ("Allgemeinstromzähler")
        :param str group_production_meter_id_first: the group's first
        production meter id
        :param str group_production_meter_id_second: the group's second
        production meter id
        """

        self.name = name
        self.group_meter_id = group_meter_id
        self.group_production_meter_id_first = group_production_meter_id_first
        self.group_production_meter_id_second = group_production_meter_id_second
