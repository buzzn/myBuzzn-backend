import os
from pathlib import Path
import time
from datetime import datetime, timedelta
import logging
from discovergy.discovergy import Discovergy
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.group import Group


logger = logging.getLogger(__name__)
client_name = 'BuzznClient'
email = os.environ['DISCOVERGY_EMAIL']
password = os.environ['DISCOVERGY_PASSWORD']


def create_session():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_all_meter_ids(session):
    """ Get all meter ids from sqlite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]\
        + [group_meter_id[0]
           for group_meter_id in session.query(Group.group_meter_id).all()]


def calc_end():
    """ Calculate timestamp of end of interval. """

    return round(datetime.now().timestamp() * 1e3)


def calc_one_year_back():
    """ Calculate timestamp of one year back in time. """

    return round((datetime.now() - timedelta(days=365)).timestamp() * 1e3)


def calc_one_week_back():
    """ Calculate timestamp of one week back in time. """

    return round((datetime.now() - timedelta(days=7)).timestamp() * 1e3)


def calc_two_days_back():
    """ Calculate timestamp of 24 hours back in time. """

    return round((datetime.now() - timedelta(hours=48)).timestamp() * 1e3)


class Task:
    """ Handle discovergy login, data retrieval, populating and updating the
    redis database. """

    def __init__(self):
        self.d = Discovergy(client_name)
        self.redis_db = redis.Redis(
            host='localhost', port=6379, db=0)  # connect to server

    def login(self):
        """ Authenticate against the discovergy backend. """

        self.d.login(email, password)

    def populate_redis(self):
        """ Populate the redis database with all discovergy data from the past. """

        all_readings = list()
        all_disaggregations = list()

        try:
            # Flush all keys from server
            self.redis_db.flushdb()

            # Connect to sqlite database
            session = create_session()

            all_meter_ids = get_all_meter_ids(session)
            end = calc_end()
            one_year_back = calc_one_year_back()
            one_week_back = calc_one_week_back()

            # Authenticate against the discovergy backend
            self.login()

            for meter_id in all_meter_ids:
                # Get all readings for all meters from one year back until now with
                # one-week interval (this is the finest granularity we get for one
                # year back in time, cf. https://api.discovergy.com/docs/)
                for reading in self.d.get_readings(meter_id, one_year_back, end,
                                                   'one_week'):
                    all_readings.append(dict(meter_id=meter_id,
                                             time=reading['time'],
                                             values=reading['values']))

                # Get all disaggregations for all meters from one week back
                # until now. This is the earliest data we get, otherwise you'll
                # end up with a '400 Bad Request: Duration of the data
                # cannot be larger than 1 week. Please try for a smaller duration.'
                disaggregation = self.d.get_disaggregation(
                    meter_id,
                    one_week_back, end)
                for timestamp in disaggregation:
                    all_disaggregations.append(dict(meter_id=meter_id,
                                                    time=timestamp,
                                                    values=disaggregation[timestamp]))

            # pylint: disable=fixme
            # TODO - Write all values to redis database

        except Exception as e:
            logger.error("Exception: %s", e)

    def update_redis(self):
        """ Update the redis database every 60s with the latest discovergy
        data. """

        while True:
            time.sleep(60)
            latest_readings = list()
            latest_disaggregations = list()

            try:
                # Connect to sqlite database
                session = create_session()

                all_meter_ids = get_all_meter_ids(session)
                end = calc_end()
                two_days_back = calc_two_days_back()
                for meter_id in all_meter_ids:

                    # Get last reading for all meters
                    reading = self.d.get_last_reading(meter_id)
                    latest_readings.append(dict(meter_id=meter_id,
                                                time=reading['time'],
                                                values=reading['values']))

                    # Get latest disaggregation for all meters
                    disaggregation = self.d.get_disaggregation(
                        meter_id, two_days_back, end)
                    timestamps = sorted(disaggregation.keys())
                    if len(timestamps) > 0:
                        latest_disaggregations.append(dict(meter_id=meter_id,
                                                           time=timestamps[-1],
                                                           values=disaggregation[timestamps[-1]]))

                print(latest_readings)
                print(latest_disaggregations)

                # pylint: disable=fixme
                # TODO - Write all values to redis database

            except Exception as e:
                logger.error("Exception: %s", e)


if __name__ == '__main__':
    task = Task()
    task.populate_redis()
    task.update_redis()
