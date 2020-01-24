# from flask import current_app as app
from util.database import db


class LoadProfile(db.Model):
    """ Represents the standard load profile. """

    date = db.Column(db.String(33), primary_key=True)
    time = db.Column(db.String(33), primary_key=True)
    energy = db.Column(db.Float)
