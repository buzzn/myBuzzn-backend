from sqlalchemy import ForeignKey
from util.database import db


class PKV(db.Model):
    """ Represents a user's Pro-Kopf-Verbrauch (PKV) in the backend. """

    date = db.Column(db.DateTime, primary_key=True)
    meter_id = db.Column(db.String(32), ForeignKey('user.meter_id'),
                         primary_key=True)
    consumption = db.Column(db.Float)
    consumption_cumulated = db.Column(db.Float)
    inhabitants = db.Column(db.Integer, ForeignKey('user.inhabitants'))
    pkv = db.Column(db.Float)
    pkv_cumulated = db.Column(db.Float)
    days = db.Column(db.Integer)
    moving_average = db.Column(db.Float)
    moving_average_annualized = db.Column(db.Integer)

    # pylint: disable=too-many-arguments
    def __init__(self, date, meter_id, consumption, consumption_cumulated,
                 inhabitants, pkv, pkv_cumulated, days, moving_average,
                 moving_average_annualized):
        """ Creates a new user PKV entry.
        :param datetime.date date: the calculation day
        :param str meter_id: the user's meter id
        :param float consumption: the last meter reading of the calculation day
        (kWh)
        :param float consumption_cumulated: consumption_cumulated of the
        day before + the consumption (kWh)
        :param int inhabitants: the number of people living in the user's flat
        :param float pkv_cumulated: pkv_cumulated of the day before + pkv (kWh)
        :param float pkv: the Pro-Kopf-Verbrauch (kWh)
        :param int days: days of the day before + 1
        :param float moving_average: pkv_cumulated/days (kWh)
        :param int moving_average_annualized: moving_average * 365 (rounded)
        """

        self.date = date
        self.meter_id = meter_id
        self.consumption = consumption
        self.consumption_cumulated = consumption_cumulated
        self.inhabitants = inhabitants
        self.pkv = pkv
        self.pkv_cumulated = pkv_cumulated
        self.days = days
        self.moving_average = moving_average
        self.moving_average_annualized = moving_average_annualized
