from sqlalchemy import ForeignKey
from util.database import db


class BaseLine(db.Model):
    """ Represents a user's baseline in the backend. """

    timestamp = db.Column(db.DateTime, primary_key=True)
    meter_id = db.Column(db.String(32), ForeignKey('user.meter_id'),
                         primary_key=True)
    baseline = db.Column(db.Integer)

    def __init__(self, timestamp, meter_id, baseline):
        """ Creates a new user baseline.
        :param datetime.datetime timestamp: the UTC datetime
        :param str meter_id: the user's meter id
        :param float baseline: the user's baseline
        """

        self.timestamp = timestamp
        self.meter_id = meter_id
        self.baseline = baseline
