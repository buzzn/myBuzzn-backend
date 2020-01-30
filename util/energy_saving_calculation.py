# energy_consumption_last_term: The last meter reading minus the first meter
# reading of the previous term.
# energy_consumption_ongoing_term: The latest meter reading minus the first meter
# reading of the ongoing term.
# Then the estimated power consumption: (1 - ratio_values) *
# energy_consumption_last_term + energy_consumption_ongoing_term

# To get the estimated saving do: energy_consumption_last_term - estimated power consumption

# To get the estimated saving for all users sum up all last term power
# consumptions and subtract all estimated power consumptions.

# The algorithm may run once a day and store the result for each user.


from datetime import datetime
import os
from pathlib import Path
import logging
import redis
from sqlalchemy import create_engine
from util.error import exception_message


logging.basicConfig()
logger = logging.getLogger('util/energy_saving_calculation')
logging.getLogger().setLevel(logging.INFO)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']


def get_engine():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    return engine


def calc_ratio_values(start):
    """ Calculates the percentages of energy consumption for the specified
    term. A term is a year where the start may be specified by the caller.
    :param datetime.date start: the start value for the term
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


def calc_energy_consumption_last_term(start, meter_id):
    """ Calculate the last meter reading minus the first meter reading of the
    previous term for a given meter id.
    :param datetime.date start: the start value of the ongoing term
    :param str meter_id: the meter id
    :return: the last meter reading minus the first meter reading of the given
    meter id
    :rtype: float
    """
    print(start)
    print(meter_id)


def calc_energy_consumption_ongoing_term(start, meter_id):
    """ Calculate the latest meter reading minus the first meter reading of the
    ongoing term for a given meter id.
    :param datetime.date start: the start value of the ongoing term
    :param datetime meter_id: the meter id
    :return: the latest meter reading minus the first meter reading of the
    given meter id
    :rtype: float
    """
    print(start)
    print(meter_id)


def calc_estimated_energy_consumption(ratio_values, energy_consumption_last_term,
                                      energy_consumption_ongoing_term):
    """ Calculate the estimated energy saving for one user in a given term
    using the standard load profile.
    :param float ratio_values: sum of all standard load profile ratio values of the given term
    :param float energy_consumption_last_term: the last meter reading minus the
    first meter reading of the previous term
    :param float energy_consumption_ongoing_term: the last meter reading minus
    the first meter reading of the ongoing term
    :returns: the estimated energy consumption
    :rtype: float
    """

    print(ratio_values)
    print(energy_consumption_last_term)
    print(energy_consumption_ongoing_term)


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

    def calculate_energy_saving_one_user(self, start, meter_id):
        """ Calculate the estimated energy saving for one user in a given term
        using the standard load profile.
        :param datetime.date start: the start of the term
        :param str meter_id: the user's meter id
        :returns: the estimated energy saving for all users
        :rtype: int
        """

    def calculate_energy_saving_all_users(self, start):
        """ Calculate the estimated energy saving for all users in a given term
        using the standard load profile.
        :param datetime.date start: the start of the term
        :returns: the estimated energy saving for all users
        :rtype: int
        """


def run():
    """ Runs the task which calculates the estimated energy saving for all
    users and writes the results to the redis database. """

    # task = Task()
    calc_ratio_values(datetime(2020, 1, 1).date())


if __name__ == '__main__':
    run()
