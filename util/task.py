import os
import time
# from datetime import datetime, timedelta
import logging
from discovergy.discovergy import Discovergy
import eventlet


logger = logging.getLogger(__name__)
eventlet.monkey_patch()


def login(client_name):
    """ Authenticate against the discovergy backend. """

    d = Discovergy(client_name)
    d.login(os.environ['DISCOVERGY_EMAIL'], os.environ['DISCOVERGY_PASSWORD'])
    return d


def populate_redis(redis_db, all_meter_ids, client_name):
    """ Populate the redis database with all discovergy data from the past.
    :param discovergy.discovergy.Discovergy discovergy_handler: the app's discovergy handler
    :param redis.Redis redis_db: the app's redis database client
    :param list all_meter_ids: the meter ids of all users and the group meter
    ids of all groups from the sqlite database
    """

    # Flush all keys from server
    redis_db.flushdb()

    # Authenticate against the discovergy backend
    d = login(client_name)

    # Get all readings for all meters from one year back until now with
    # interval one_hour
    # now = round(datetime.now().timestamp() * 1e3)
    # begin = round((datetime.now() - timedelta(days=365)).timestamp() * 1e3)
    # for meter_id in all_meter_ids:
    # readings = discovergy_handler.get_readings(meter_id, begin, now,
    # 'one_hour')

    # Get all disaggregations for all meters from one year back until now


def update_redis(discovergy_handler, redis_db):
    """ Update the redis database every 60s with the latest discovergy data. """

    while True:
        time.sleep(60)

        # Get last reading for all meters
        # Get latest disaggregation
        print('Updating redis database with the latest discovergy data.')
