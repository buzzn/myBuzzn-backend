from datetime import datetime, timedelta
import os
import logging.config
import redis
from util.error import exception_message
from util.database import get_engine
from util.redis_helpers import get_last_meter_reading_date


logger = logging.getLogger(__name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def calc_ratio_values(start):
    """ Calculates the percentages of energy consumption for the specified
    term. A term is a year where the start may be specified by the caller.
    :param datetime.date start: the start date of the term
    :returns: sum of all standard load profile ratio values of the given term
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
            energy_total = con.execute("SELECT SUM(energy) FROM loadprofile WHERE date BETWEEN \'"
                                       + str(start) + "\' AND \'" + str(end) +
                                       '\' ORDER BY date').first()[0]

            # Query sum of energy promilles
            energy_promille = con.execute("SELECT SUM(energy) FROM loadprofile"
                                          + " WHERE date BETWEEN \'" +
                                          str(start) + "\' AND \'"
                                          + str(term_end) + '\' ORDER BY date').first()[0]

        if (energy_promille is not None) and (energy_total is not None):
            ratio_values = energy_promille/energy_total

    except Exception as e:
        message = exception_message(e)
        logger.error(message)

    return ratio_values


def calc_energy_consumption_last_term(meter_id, start):
    """ Calculate the last meter reading minus the first meter reading of the
    previous term for a given meter id.
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the ongoing term
    :returns: the last meter reading minus the first meter reading of the given
    meter id or None if there are no values
    :rtype: int or type(None)
    """

    begin = (datetime(start.year - 1, start.month, start.day)).date()
    end = start - timedelta(days=1)
    last_meter_reading = get_last_meter_reading_date(redis_client, meter_id,
                                                     datetime.strftime(end, '%Y-%m-%d'))
    first_meter_reading = get_last_meter_reading_date(redis_client, meter_id,
                                                      datetime.strftime(begin, '%Y-%m-%d'))

    if last_meter_reading is None or first_meter_reading is None:
        message = 'No energy consumption available for {} between {} and {}'.format(
            meter_id, str(begin), str(end))
        logger.info(message)
        return None

    return last_meter_reading - first_meter_reading


def calc_energy_consumption_ongoing_term(meter_id, start):
    """ Calculate the latest meter reading minus the first meter reading of the
    ongoing term for a given meter id.
    :param datetime meter_id: the meter id
    :param datetime.date start: the start date of the ongoing term
    :returns: the latest meter reading minus the first meter reading of the
    given meter id or None if there are no values
    :rtype: int or type(None)
    """

    end = datetime.utcnow().date()
    last_meter_reading = get_last_meter_reading_date(redis_client, meter_id,
                                                     datetime.strftime(end, '%Y-%m-%d'))
    first_meter_reading = get_last_meter_reading_date(redis_client, meter_id,
                                                      datetime.strftime(start, '%Y-%m-%d'))

    if last_meter_reading is None or first_meter_reading is None:
        message = 'No energy consumption available for {} between {} and {}'.format(
            meter_id, str(start), str(end))
        logger.info(message)
        return None

    return last_meter_reading - first_meter_reading


def calc_estimated_energy_consumption(meter_id, start):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile as
    (1 - ratio values) * energy consumption last term + energy consumption ongoing term
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the given term
    :returns: the estimated energy consumption or None if there are no values
    :rtype: float or type(None)
    """

    ratio_values = calc_ratio_values(start)
    energy_consumption_last_term = calc_energy_consumption_last_term(meter_id, start)
    energy_consumption_ongoing_term = calc_energy_consumption_ongoing_term(meter_id, start)

    if energy_consumption_last_term is None or energy_consumption_ongoing_term is None:
        message = 'No estimated energy consumption available for meter_id {} from {} on'.format(
            meter_id, str(start))
        logger.info(message)
        return None

    return (1 - ratio_values) * energy_consumption_last_term + energy_consumption_ongoing_term


def calc_estimated_energy_saving(meter_id, start):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile.
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the given term
    :returns: the estimated energy saving
    :rtype: float or None if there are no values
    """

    energy_consumption_last_term = calc_energy_consumption_last_term(meter_id, start)
    estimated_energy_consumption = calc_estimated_energy_consumption(meter_id, start)
    if energy_consumption_last_term is None or estimated_energy_consumption is None:
        message = 'No estimated energy saving available for meter_id {} from {} on'.format(
            meter_id, str(start))
        logger.info(message)
        return None

    return energy_consumption_last_term - estimated_energy_consumption
