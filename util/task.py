import os
import time
# from datetime import datetime, timedelta
import logging
from discovergy.discovergy import Discovergy
import redis


logger = logging.getLogger(__name__)
client_name = 'BuzznClient'
email = os.environ['DISCOVERGY_EMAIL']
password = os.environ['DISCOVERGY_PASSWORD']


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

        # Flush all keys from server
        self.redis_db.flushdb()

        # Authenticate against the discovergy backend
        self.login()

        # Get all readings for all meters from one year back until now with
        # interval one_hour

        # now = round(datetime.now().timestamp() * 1e3)
        # begin = round((datetime.now() - timedelta(days=365)).timestamp() * 1e3)

        # Get all disaggregations for all meters from one year back until now

        # all_meter_ids = [meter_id[0] for meter_id in sqlite_db.session.query(User.meter_id).all(
        # )] + [group_meter_id[0] for group_meter_id in sqlite_db.session.query(Group.group_meter_id).all()]


def update_redis():
    """ Update the redis database every 60s with the latest discovergy data. """

    while True:
        time.sleep(60)

        # Get last reading for all meters
        # Get latest disaggregation
        print('Updating redis database with the latest discovergy data.')


if __name__ == '__main__':
    task = Task()
    task.populate_redis()
    while True:
        task.update_redis()
