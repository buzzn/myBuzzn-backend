from datetime import datetime, time, timedelta
import json
import os
import logging
from dateutil import parser
import redis
import pytz
from models.user import User
from util.error import exception_message
from util.database import create_session, get_engine
from util.redis_helpers import get_sorted_keys


logging.basicConfig()
logger = logging.getLogger('util/energy_saving_calculation')
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_all_user_meter_ids(session):
    """ Get all user meter ids from sqlite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]


def calc_ratio_values(start):
    """ Calculates the percentages of energy consumption for the specified
    term. A term is a year where the start may be specified by the caller.
    :param datetime.date start: the start date of the term
    :return: sum of all standard load profile ratio values of the given term
    :rtype: float
    """

    end = datetime(start.year + 1, start.month, start.day).date()
    term_end = datetime.utcnow().date()
    engine = get_engine()
    energy_total = 0.0
    ratio_values = 0.0
    try:
        with engine.connect() as con:
            # Query total energy which should be ~ 1.000.000 kWh
            rs = con.execute("SELECT SUM(energy) FROM loadprofile WHERE date BETWEEN \'" +
                             str(start) + "\' AND \'" + str(end) + '\' ORDER BY date')
            energy_total = rs.first()[0]

            # Query sum of energy promilles
            rs = con.execute("SELECT SUM(energy) FROM loadprofile WHERE date BETWEEN \'" +
                             str(start) + "\' AND \'" + str(term_end) + '\' ORDER BY date')
            energy_promille = rs.first()[0]
            ratio_values = energy_promille/energy_total

    except Exception as e:
        message = exception_message(e)
        logger.error(message)

    return ratio_values


def get_meter_reading_date(meter_id, date):
    """ Return the last reading for the given meter id on the given day which
    is stored in the redis database. As we were using unix timestamps as basis
    for our dates all along, there is no need to convert the given,
    timezone-unaware date to UTC.
    :param str meter_id: the meter id for which to get the value
    :param datetime.date date: the date for which to get the value
    :return: the first reading for the given meter id on the given date
    :rtype: float or None if there are no values
    """

    readings = []
    data = None
    naive_begin = datetime.combine(date, time(0, 0, 0))
    naive_end = datetime.combine(date, time(23, 59, 59))
    timezone = pytz.timezone('UTC')
    begin = (timezone.localize(naive_begin)).timestamp()
    end = (timezone.localize(naive_end)).timestamp()

    for key in get_sorted_keys(redis_client, meter_id):
        try:
            data = json.loads(redis_client.get(key))
        except Exception as e:
            message = exception_message(e)
            logger.error(message)
        if data is not None:
            if data.get('type') == 'reading':
                reading_date = parser.parse(key[len(meter_id)+1:])
                reading_timestamp = reading_date.timestamp()
                if begin <= reading_timestamp <= end:
                    readings.append(data.get('values')['energy'])

    if len(readings) > 0:
        return readings[-1]

    logger.info('No last reading available for meter id %s on %s',
                meter_id, str(date))
    return None


def calc_energy_consumption_last_term(meter_id, start):
    """ Calculate the last meter reading minus the first meter reading of the
    previous term for a given meter id.
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the ongoing term
    :return: the last meter reading minus the first meter reading of the given
    meter id
    :rtype: int or None if there are no values
    """

    begin = (datetime(start.year - 1, start.month, start.day)).date()
    end = start - timedelta(days=1)
    last_meter_reading = get_meter_reading_date(meter_id, end)
    first_meter_reading = get_meter_reading_date(meter_id, begin)

    if last_meter_reading is None or first_meter_reading is None:
        logger.info('No energy consumption available for %s between %s and %s',
                    meter_id, str(begin), str(end))
        return None

    return last_meter_reading - first_meter_reading


def calc_energy_consumption_ongoing_term(meter_id, start):
    """ Calculate the latest meter reading minus the first meter reading of the
    ongoing term for a given meter id.
    :param datetime meter_id: the meter id
    :param datetime.date start: the start date of the ongoing term
    :return: the latest meter reading minus the first meter reading of the
    given meter id
    :rtype: int or None if there are no values
    """

    end = datetime.utcnow().date()
    last_meter_reading = get_meter_reading_date(meter_id, end)
    first_meter_reading = get_meter_reading_date(meter_id, start)

    if last_meter_reading is None or first_meter_reading is None:
        logger.info('No energy consumption available for %s between %s and %s',
                    meter_id, str(start), str(end))
        return None

    return last_meter_reading - first_meter_reading


def calc_estimated_energy_consumption(meter_id, start):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile as
    (1 - ratio values) * energy consumption last term + energy consumption ongoing term
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the given term
    :returns: the estimated energy consumption
    :rtype: float or None if there are no values
    """

    ratio_values = calc_ratio_values(start)
    energy_consumption_last_term = calc_energy_consumption_last_term(meter_id,
                                                                     start)
    energy_consumption_ongoing_term = calc_energy_consumption_ongoing_term(
        meter_id, start)

    if energy_consumption_last_term is None or energy_consumption_ongoing_term is None:
        logger.info(
            'No estimated energy consumption available for meter_id %s from\
 %s on', meter_id, str(start))
        return None

    return (1 - ratio_values) * energy_consumption_last_term + energy_consumption_ongoing_term


def calc_estimated_energy_saving(meter_id, start):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile.
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the given term
    :return: the estimated energy saving
    :rtype: float or None if there are no values
    """

    energy_consumption_last_term = calc_energy_consumption_last_term(meter_id,
                                                                     start)
    estimated_energy_consumption = calc_estimated_energy_consumption(meter_id,
                                                                     start)
    if energy_consumption_last_term is None or estimated_energy_consumption is None:
        logger.info(
            'No estimated energy saving available for meter_id %s from\
 %s on', meter_id, str(start))
        return None

    return energy_consumption_last_term - estimated_energy_consumption


def estimate_energy_saving_each_user(start):
    """ Calculate the estimated energy saving for each user.
    :param datetime.date start: the start date of the given term
    :return: the estimated energy saving of each user in the given term
    :rtype: dict
    """

    savings = dict()
    session = create_session()
    for meter_id in get_all_user_meter_ids(session):
        saving = calc_estimated_energy_saving(meter_id, start)
        savings[meter_id] = saving

    return savings


def estimate_energy_saving_all_users(start):
    """ Calculate the estimated energy saving of all users by summing up all
    last term energy consumptions and subtracting all estimated energy
    consumptions.
    :param datetime.date start: the start date of the given term
    :return: the estimated energy saving of all users in the given term
    :rtype: float
    """

    savings = 0.0
    session = create_session()
    for meter_id in get_all_user_meter_ids(session):
        saving = calc_estimated_energy_saving(meter_id, start)
        if saving is not None:
            savings += saving

    return savings
