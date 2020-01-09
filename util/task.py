import json
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
from error import MISSING_DISCOVERGY_CREDENTIALS


logger = logging.getLogger(__name__)
client_name = 'BuzznClient'
email = os.environ['DISCOVERGY_EMAIL']
password = os.environ['DISCOVERGY_PASSWORD']
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


def get_all_meter_ids(session):
    """ Get all meter ids from sqlite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]\
        + [group_meter_id[0]
           for group_meter_id in session.query(Group.group_meter_id).all()]


def calc_end():
    """ Calculate timestamp of end of interval. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round(datetime.now().timestamp() * 1000)


def calc_one_year_back():
    """ Calculate timestamp of one year back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.now() - timedelta(days=365)).timestamp() * 1000)


def calc_one_week_back():
    """ Calculate timestamp of one week back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.now() - timedelta(days=7)).timestamp() * 1000)


def calc_two_days_back():
    """ Calculate timestamp of 24 hours back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.now() - timedelta(hours=48)).timestamp() * 1000)


class Task:
    """ Handle discovergy login, data retrieval, populating and updating the
    redis database. """

    def __init__(self):
        self.d = Discovergy(client_name)
        self.redis_client = redis.Redis(
            host='localhost', port=6379, db=0)  # connect to server

    def login(self):
        """ Authenticate against the discovergy backend. """

        self.d.login(email, password)

    def populate_redis(self):
        """ Populate the redis database with all discovergy data from the past. """

        # Flush all keys from server
        self.redis_client.flushdb()

        # Connect to sqlite database
        session = create_session()

        all_meter_ids = get_all_meter_ids(session)
        end = calc_end()
        one_year_back = calc_one_year_back()
        one_week_back = calc_one_week_back()

        try:
            # Authenticate against the discovergy backend
            self.login()

            # Get all readings for all meters from one year back until now with
            # one-week interval (this is the finest granularity we get for one
            # year back in time, cf. https://api.discovergy.com/docs/)
            for meter_id in all_meter_ids:
                for reading in self.d.get_readings(meter_id, one_year_back, end,
                                                   'one_week'):
                    key = meter_id + str(reading['time'])

                    # Write reading to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars) and the
                    # timestamp (16 chars)
                    self.redis_client.set(key, json.dumps(reading['values']))

                # Get all disaggregations for all meters from one week back
                # until now. This is the earliest data we get, otherwise you'll
                # end up with a '400 Bad Request: Duration of the data
                # cannot be larger than 1 week. Please try for a smaller duration.'
                disaggregation = self.d.get_disaggregation(
                    meter_id, one_week_back, end)
                for timestamp in disaggregation:

                    # Write measurement to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars) and the
                    # timestamp (16 chars)
                    key = meter_id + timestamp
                    self.redis_client.set(
                        key, json.dumps(disaggregation[timestamp]))
            return True

        except Exception as e:
            logger.error('Exception: %s', e)
            return MISSING_DISCOVERGY_CREDENTIALS

    def update_redis(self):
        """ Update the redis database every 60s with the latest discovergy
        data. """

        while True:
            time.sleep(60)

            try:
                # Connect to sqlite database
                session = create_session()

                all_meter_ids = get_all_meter_ids(session)
                end = calc_end()
                two_days_back = calc_two_days_back()

                # Get last reading for all meters
                for meter_id in all_meter_ids:
                    reading = self.d.get_last_reading(meter_id)
                    key = meter_id + str(reading['time'])

                    # Write reading to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars) and the
                    # timestamp (16 chars)
                    self.redis_client.set(key, json.dumps(reading['values']))

                    # Get latest disaggregation for all meters
                    disaggregation = self.d.get_disaggregation(
                        meter_id, two_days_back, end)
                    timestamps = sorted(disaggregation.keys())
                    if len(timestamps) > 0:
                        key = meter_id + timestamps[-1]

                        # Write measurement to redis database as key-value-pair
                        # The unique key consists of the meter id (16 chars) and the
                        # timestamp (16 chars)
                        self.redis_client.set(
                            key, json.dumps(disaggregation[timestamps[-1]]))

            except Exception as e:
                logger.error("Exception: %s", e)


if __name__ == '__main__':
    task = Task()
    redis_state = task.populate_redis()
    if redis_state is not True:
        logger.error(redis_state.description)
    task.update_redis()
