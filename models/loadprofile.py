from util.database import db


class LoadProfile(db.Model):
    """ Represents the standard load profile. """

    __tablename__ = 'loadprofile'
    date = db.Column(db.String(33), primary_key=True)
    time = db.Column(db.String(33), primary_key=True)
    energy = db.Column(db.Float)

    def __init__(self, date, time, energy):
        self.date = date
        self.time = time
        self.energy = energy
