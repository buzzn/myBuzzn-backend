
# To get the estimated saving do: energy_consumption_last_term - estimated power consumption

# To get the estimated saving for all users sum up all last term power
# consumptions and subtract all estimated power consumptions.

# The algorithm may run once a day and store the result for each user.


from datetime import datetime, time, timedelta
import json
import os
from pathlib import Path
import logging
from dateutil import parser
import redis
from sqlalchemy import create_engine
import pytz
from util.error import exception_message


logging.basicConfig()
logger = logging.getLogger('util/energy_saving_calculation')
logging.getLogger().setLevel(logging.INFO)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_engine():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    return engine


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
            rs = con.execute("SELECT * FROM loadprofile WHERE date BETWEEN \'" +
                             str(start) + "\' AND \'" + str(end) + '\' ORDER BY date')

            # Calculate energy total which should be ~1.000.000 kWh
            for row in rs:
                energy_total += row[2]

            # Calculate 1% of energy total
            energy_percent = energy_total/100

            # Calculate percentage of each energy value and write to result
            rs = con.execute("SELECT * FROM loadprofile WHERE date BETWEEN \'" +
                             str(start) + "\' AND \'" + str(term_end) + '\' ORDER BY date')
            for row in rs:
                percentage = float(row[2])/energy_percent
                ratio_values += percentage

    except Exception as e:
        message = exception_message(e)
        logger.error(message)

    return ratio_values


def get_sorted_keys(meter_id):
    """ Return all keys stored in the redis db for a given meter id.
    :param str meter_id: the meter id to prefix the scan with
    """

    return sorted([key.decode('utf-8') for key in redis_client.scan_iter(meter_id + '*')])


def get_meter_reading_date(meter_id, date):
    """ Return the last reading for the given meter id on the given day which
    is stored in the redis database. As we were using unix timestamps as basis
    for our dates all along, there is no need to convert the given,
    timezone-unaware date to UTC.
    :param str meter_id: the meter id for which to get the value
    :param datetime.date date: the date for which to get the value
    :return: the first reading for the given meter id on the given date
    :rtype: float
    """

    result = 0.0
    readings = []
    naive_begin = datetime.combine(date, time(0, 0, 0))
    naive_end = datetime.combine(date, time(23, 59, 59))
    timezone = pytz.timezone('UTC')
    begin = (timezone.localize(naive_begin)).timestamp()
    end = (timezone.localize(naive_end)).timestamp()

    try:
        for key in get_sorted_keys(meter_id):
            data = json.loads(redis_client.get(key))
            if data.get('type') == 'reading':
                reading_date = parser.parse(key[len(meter_id)+1:])
                reading_timestamp = reading_date.timestamp()
                if begin <= reading_timestamp <= end:
                    readings.append(data.get('values')['energy'])
        result = readings[-1]

    except Exception as e:
        message = exception_message(e)
        logger.error(message)

    return result


def calc_energy_consumption_last_term(meter_id, start):
    """ Calculate the last meter reading minus the first meter reading of the
    previous term for a given meter id.
    :param str meter_id: the meter id
    :param datetime.date start: the start date of the ongoing term
    :return: the last meter reading minus the first meter reading of the given
    meter id
    :rtype: float
    """

    begin = (datetime(start.year - 1, start.month, start.day)).date()
    end = start - timedelta(days=1)
    last_meter_reading = get_meter_reading_date(meter_id, end)
    first_meter_reading = get_meter_reading_date(meter_id, begin)
    return last_meter_reading - first_meter_reading


def calc_energy_consumption_ongoing_term(meter_id, start):
    """ Calculate the latest meter reading minus the first meter reading of the
    ongoing term for a given meter id.
    :param datetime meter_id: the meter id
    :param datetime.date start: the start date of the ongoing term
    :return: the latest meter reading minus the first meter reading of the
    given meter id
    :rtype: float
    """

    end = datetime.utcnow().date()
    last_meter_reading = get_meter_reading_date(meter_id, end)
    first_meter_reading = get_meter_reading_date(meter_id, start)
    return last_meter_reading - first_meter_reading


def calc_estimated_energy_consumption(meter_id, start):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile as
    (1 - ratio values) * energy consumption last term + energy consumption ongoing term
    :param datetime.date start: the start date of the given term
    :returns: the estimated energy consumption
    :rtype: float
    """

    ratio_values = calc_ratio_values(start)
    energy_consumption_last_term = calc_energy_consumption_last_term(meter_id,
                                                                     start)
    energy_consumption_ongoing_term = calc_energy_consumption_ongoing_term(
        meter_id, start)
    return (1 - ratio_values) * energy_consumption_last_term + energy_consumption_ongoing_term


def calc_estimated_energy_saving(energy_consumption_last_term,
                                 estimated_energy_consumption):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile.
    :param float energy_consumption_last_term: the last meter reading minus the first meter reading
    :param float estimated_energy_consumption: the estimated energy consumption
    :return: the estimated energy saving
    :rtype: float
    """

    print(energy_consumption_last_term)
    print(estimated_energy_consumption)


def estimated_energy_saving_all_users():
    """ Calculate the estimated energy saving of all users by summing up all
    last term energy consumptions and subtracting all estimated energy
    consumptions.
    :return: the estimated energy saving of all users
    :rtype: float
    """


class Task:
    """ Retrieve standard load profile from sqlite database, calculate
    estimated energy saving for each user and all users, write results to redis database. """

    def __init__(self):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port,
                                        db=redis_db)  # connect to server


def run():
    """ Runs the task which calculates the estimated energy saving for all
    users and writes the results to the redis database. """

    # task = Task()
    date = datetime(2020, 1, 30).date()
    calc_estimated_energy_consumption(
        'b4234cd4bed143a6b9bd09e347e17d34', date)


if __name__ == '__main__':
    run()
