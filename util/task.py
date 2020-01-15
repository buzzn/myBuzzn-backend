import json
import os
from pathlib import Path
import time as stdlib_time
from datetime import datetime, timedelta, date, time
import logging
from discovergy.discovergy import Discovergy
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.group import Group

logging.basicConfig()
logger = logging.getLogger('util/task')
logging.getLogger().setLevel(logging.INFO)
client_name = 'BuzznClient'
email = os.environ['DISCOVERGY_EMAIL']
password = os.environ['DISCOVERGY_PASSWORD']
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
last_data_flush = None


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
    return round(datetime.utcnow().timestamp() * 1000)


def calc_one_year_back():
    """ Calculate timestamp of one year back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.utcnow() - timedelta(days=365)).timestamp() * 1000)


def calc_support_year_start():
    """ Calculate start of BAFA support year.
    :return:
    March, 12th the year before if today is between January, 1st and March, 11th
    March, 12th of the current year otherwise
    :rtype: unix timestamp in milliseconds
    """

    now = datetime.utcnow()
    start_day = 12
    start_month = 3
    if (now.month < start_month) or (now.month == start_month and now.day <
                                     start_day):
        start_year = now.year - 1
    else:
        start_year = now.year
    d = date(start_year, start_month, start_day)
    t = time(0, 0)
    support_year_start = round(datetime.combine(d, t).timestamp() * 1000)
    return support_year_start


def calc_support_week_start():
    """ Calculate start of BAFA support week.
    :return:
    March, 12th of the current year if today is between March, 12th
    and March, 18th
    7 days back in time otherwise
    :rtype: unix timestamp in milliseconds
    """

    now = datetime.utcnow()
    if (now.month == 3) and (11 < now.day < 19):
        d = date(now.year, 3, 12)
    else:
        d = (now - timedelta(days=7)).date()
    t = now.time()
    support_week_start = round(datetime.combine(d, t).timestamp() * 1000)
    return support_week_start


def calc_one_week_back():
    """ Calculate timestamp of one week back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.utcnow() - timedelta(days=7)).timestamp() * 1000)


def calc_two_days_back():
    """ Calculate timestamp of 48 hours back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.utcnow() - timedelta(hours=48)).timestamp() * 1000)


class Task:
    """ Handle discovergy login, data retrieval, populating and updating the
    redis database. """

    def __init__(self):
        self.d = Discovergy(client_name)
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)  # connect to server

    def login(self):
        """ Authenticate against the discovergy backend. """

        self.d.login(email, password)

    def populate_redis(self):
        """ Populate the redis database with all discovergy data from the past.
        :return: An error if something went wrong, None otherwise
        :rtype: util.error.Error if something went wrong, NoneType otherwise
        """

        # pylint: disable=global-statement
        global last_data_flush
        last_data_flush = datetime.utcnow()

        # Flush all keys from server
        self.redis_client.flushdb()

        # Connect to sqlite database
        session = create_session()

        all_meter_ids = get_all_meter_ids(session)
        end = calc_end()
        disaggregation_start = calc_support_week_start()
        readings_start = calc_support_year_start()

        try:
            # Authenticate against the discovergy backend
            self.login()

        except Exception as e:
            logger.error('Exception: %s', e)
            logger.error('Wrong or missing discovergy credentials.')
            return

        for meter_id in all_meter_ids:
            try:
                # Get all readings for all meters from one the beginning of the
                # BAFA support year until now with
                # one-week interval (this is the finest granularity we get for one
                # year back in time, cf. https://api.discovergy.com/docs/)
                readings = self.d.get_readings(meter_id, readings_start, end,
                                               'one_week')

                if readings == []:
                    logger.info("No readings available for metering id %s",
                                meter_id)
                    continue

                for reading in readings:
                    timestamp = reading['time']

                    # Convert unix epoch time in milliseconds to UTC format
                    new_timestamp = datetime.utcfromtimestamp(timestamp/1000).\
                        strftime('%Y-%m-%d %H:%M:%S')

                    key = meter_id + '_' + str(new_timestamp)

                    # Write reading to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars), the
                    # separator '_' and the UTC timestamp (19 chars)
                    data = dict(type='reading', values=reading['values'])
                    self.redis_client.set(key, json.dumps(data))

                # Get all disaggregation values for all meters from one week back
                # until now. This is the earliest data we get, otherwise you'll
                # end up with a '400 Bad Request: Duration of the data
                # cannot be larger than 1 week. Please try for a smaller duration.'
                # If one week back lies before the current BAFA support year
                # start, start with that value instead.
                disaggregation = self.d.get_disaggregation(
                    meter_id, disaggregation_start, end)

                if disaggregation == {}:
                    logger.info("No disaggregation available for metering id %s",
                                meter_id)
                    continue

                for timestamp in disaggregation:
                    # Convert unix epoch time in milliseconds to UTC format
                    new_timestamp = datetime.utcfromtimestamp(
                        int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')
                    key = meter_id + '_' + str(new_timestamp)

                    # Write disaggregation to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars), the
                    # separator '_' and the UTC timestamp (19 chars)
                    data = dict(type='disaggregation',
                                values=disaggregation[timestamp])
                    self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                logger.error('Exception: %s', e)

    def update_redis(self):
        """ Update the redis database every 60s with the latest discovergy
        data. """

        while True:
            stdlib_time.sleep(60)

            try:
                # Populate redis if last data flush was more than 24h ago
                # pylint: disable=global-statement
                global last_data_flush
                if (last_data_flush is None) or (datetime.utcnow() -
                                                 last_data_flush >
                                                 timedelta(hours=24)):
                    self.populate_redis()

                # Connect to sqlite database
                session = create_session()

                all_meter_ids = get_all_meter_ids(session)
                end = calc_end()
                two_days_back = calc_two_days_back()

                # Get last reading for all meters
                for meter_id in all_meter_ids:
                    reading = self.d.get_last_reading(meter_id)

                    if reading == {}:
                        logger.info("No last reading available for metering id %s",
                                    meter_id)
                        continue

                    timestamp = reading['time']
                    new_timestamp = datetime.utcfromtimestamp(timestamp/1000).\
                        strftime('%Y-%m-%d %H:%M:%S')
                    key = meter_id + '_' + str(new_timestamp)

                    # Write reading to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars), the
                    # separator '_' and the UTC timestamp (19 chars)
                    data = dict(type='reading', values=reading['values'])
                    self.redis_client.set(key, json.dumps(data))

                # Get latest disaggregation for all meters
                for meter_id in all_meter_ids:
                    disaggregation = self.d.get_disaggregation(
                        meter_id, two_days_back, end)

                    if disaggregation == []:
                        logger.info(
                            "No disaggregation available for metering id % s", meter_id)
                        continue

                    timestamps = sorted(disaggregation.keys())
                    if len(timestamps) > 0:
                        timestamp = timestamps[-1]

                        # Convert unix epoch time in milliseconds to UTC format
                        new_timestamp = datetime.utcfromtimestamp(int(timestamp)/1000).\
                            strftime('%Y-%m-%d %H:%M:%S')

                        key = meter_id + '_' + str(new_timestamp)

                        # Write disaggregation to redis database as key-value-pair
                        # The unique key consists of the meter id (16 chars), the
                        # separator '_' and the UTC timestamp (19 chars)
                        data = dict(type='disaggregation',
                                    values=disaggregation[timestamp])
                        self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                logger.error("Exception: %s", e)


def run():
    """Runs the task which fills the redis table with the latest readings."""
    task = Task()
    task.update_redis()


if __name__ == '__main__':
    run()
