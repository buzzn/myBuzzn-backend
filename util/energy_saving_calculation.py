# A Standardlastprofil is a set of pairs, where each pair specifies a time span of
# 15 minutes and the amount of energy consumed in this span. In this description
# we assume each value of the energy consumption to be between 0 and 1 and the sum
# of all values to be equal to 1. This might differ in the database.

# To get the estimated power consumption for one user within a given term do:
# ratio_values: Sum up all Standardlastprofil ratio values of the ongoing term.
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
from sqlalchemy.orm import sessionmaker
# from util.error import exception_message


logging.basicConfig()
logger = logging.getLogger('util/energy_saving_calculation')
logging.getLogger().setLevel(logging.INFO)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']


def create_session():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def calculate_percentages(start):
    """ Calculates the percentages of energy consumption for the specified
    term. A term is a year where the start may be specified by the caller.
    :param datetime.date start: the start value for the term
    :return: the energy consumption for each date
    :rtype: dict
    """

    year = start.year
    month = start.month
    day = start.day
    #  end = datetime(year + 1, month, day).date()
    return {}


class Task:
    """ Retrieve standard load profile from sqlite database, calculate
    estimated energy saving for each user and all users, write results to redis database. """

    def __init__(self):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port,
                                        db=redis_db)  # connect to server

    def calculate_energy_saving_one_user(self, user_id, start):
        """ Calculate the estimated energy saving for one user in a given term
        using the standard load profile.
        :param str user_id: the user's id
        :param datetime.date start: the start of the term
        :returns: the estimated energy saving for the user
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
    calculate_percentages(datetime.utcnow().date())


if __name__ == '__main__':
    run()
