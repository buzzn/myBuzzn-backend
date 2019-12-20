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
        """ Populate the redis database with all discovergy data from the past.
        :param redis.Redis redis_db: the app's redis database client
        :param list all_meter_ids: the meter ids of all users and the group meter
        ids of all groups from the sqlite database
        """
        all_readings = list()
        all_disaggregations = list()

        try:
            # Flush all keys from server
            self.redis_db.flushdb()

            # Connect to sqlite database
            session = create_session()

            all_meter_ids = [meter_id[0] for meter_id in session.query(User.meter_id).all(
            )] + [group_meter_id[0] for group_meter_id in session.query(Group.group_meter_id).all()]
            end = round(datetime.now().timestamp() * 1e3)
            one_year_back = round(
                (datetime.now() - timedelta(days=365)).timestamp() * 1e3)
            one_week_back = round(
                (datetime.now() - timedelta(days=7)).timestamp() * 1e3)

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

    # pylint: disable=no-self-use
    def update_redis(self):
        """ Update the redis database every 60s with the latest discovergy
        data. """
        while True:
            print('Updating redis database with the latest discovergy data.')
            time.sleep(60)

            # pylint: disable=fixme
            # TODO - Get last reading for all meters
            # TODO - Get latest disaggregation
            # TODO - Write all values to redis database


if __name__ == '__main__':
    task = Task()
    task.populate_redis()
    task.update_redis()
