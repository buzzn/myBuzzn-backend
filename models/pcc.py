from sqlalchemy import ForeignKey
from util.database import db


class PerCapitaConsumption(db.Model):
    """ Represents a user's per capita consumption in the backend. """

    date = db.Column(db.DateTime, primary_key=True)
    meter_id = db.Column(db.String(32), ForeignKey('user.meter_id'),
                         primary_key=True)
    consumption = db.Column(db.Float)
    consumption_cumulated = db.Column(db.Float)
    inhabitants = db.Column(db.Integer, ForeignKey('user.inhabitants'))
    per_capita_consumption = db.Column(db.Float)
    per_capita_consumption_cumulated = db.Column(db.Float)
    days = db.Column(db.Integer)
    moving_average = db.Column(db.Float)
    moving_average_annualized = db.Column(db.Integer)

    # pylint: disable=too-many-arguments
    def __init__(self, date, meter_id, consumption, consumption_cumulated,
                 inhabitants, per_capita_consumtion, per_capita_consumption_cumulated,
                 days, moving_average, moving_average_annualized):
        """ Creates a new user PCC entry.
        :param datetime.date date: the calculation day
        :param str meter_id: the user's meter id
        :param float consumption: the last meter reading of the calculation day
        (kWh)
        :param float consumption_cumulated: consumption_cumulated of the
        day before + the consumption (kWh)
        :param int inhabitants: the number of people living in the user's flat
        :param float per_capita_consumption_cumulated: per_capita_consumption_cumulated
        of the day before + per_capita_consumtion(kWh)
        :param float per_capita_consumtion: per capita consumption (kWh)
        :param int days: days of the day before + 1
        :param float moving_average: per_capita_consumption_cumulated/days (kWh)
        :param int moving_average_annualized: moving_average * 365 (rounded)
        """

        self.date = date
        self.meter_id = meter_id
        self.consumption = consumption
        self.consumption_cumulated = consumption_cumulated
        self.inhabitants = inhabitants
        self.per_capita_consumption = per_capita_consumtion
        self.per_capita_consumption_cumulated = per_capita_consumption_cumulated
        self.days = days
        self.moving_average = moving_average
        self.moving_average_annualized = moving_average_annualized
