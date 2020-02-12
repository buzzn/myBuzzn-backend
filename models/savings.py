from sqlalchemy import ForeignKey
from util.database import db


class UserSaving(db.Model):
    """ Represents a user savings entry in the backend. """

    timestamp = db.Column(db.DateTime, primary_key=True)
    meter_id = db.Column(db.String(32), ForeignKey('user.meter_id'),
                         primary_key=True)
    saving = db.Column(db.Float)

    def __init__(self, timestamp, meter_id, saving):
        """ Creates a new user saving.
        :param datetime.datetime timestamp: the UTC datetime
        :param int id: the user's id
        :param float saving: the user's saving
        """

        self.timestamp = timestamp
        self.meter_id = meter_id
        self.saving = saving


class CommunitySaving(db.Model):
    """ Represents a community savings entry in the backend. """

    timestamp = db.Column(db.DateTime, primary_key=True)
    saving = db.Column(db.Float)

    def __init__(self, timestamp, saving):
        """ Creates a new community saving.
        :param datetime.datetime timestamp: the UTC datetime
        :param float saving: the community saving
        """

        self.timestamp = timestamp
        self.saving = saving
