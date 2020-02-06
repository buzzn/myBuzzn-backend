from datetime import datetime, timedelta, time
import json
import logging
import os
from discovergy.discovergy import Discovergy
import redis
from util.database import create_session
from util.error import exception_message
from util.energy_saving_calculation import get_all_user_meter_ids
from util.task import calc_support_year_start


logging.basicConfig()
logger = logging.getLogger('util/energy_saving_task')
client_name = 'BuzznClient'
email = os.environ['DISCOVERGY_EMAIL']
password = os.environ['DISCOVERGY_PASSWORD']
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']


def calculate_timestamps():
    """ Calculate begin and end of previous and ongoing terms. """

    # Calculate timestamps for ongoing term
    begin_ongoing_term = calc_support_year_start()
    end_ongoing_term = round(datetime.combine(datetime.now().date(), time(0, 0,
                                                                          0)).timestamp()
                             * 1000)

    # Calculate timestamps for previous term
    end_prev_term = round((datetime.fromtimestamp(
        begin_ongoing_term/1000) - timedelta(days=1)).timestamp() * 1000)

    previous_year = datetime.fromtimestamp(
        begin_ongoing_term/1000).year - 1
    begin_previous_term_date = datetime.fromtimestamp(
        begin_ongoing_term/1000).date().replace(year=previous_year)
    begin_prev_term = round(datetime.combine(begin_previous_term_date,
                                             time(0, 0, 0)).timestamp() *
                            1000)

    return begin_ongoing_term, end_ongoing_term, begin_prev_term, end_prev_term


class Task:
    """ Handle discovergy login, data retrieval, populating and updating the
    redis database. """

    def __init__(self):
        self.d = Discovergy(client_name)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port,
                                        db=redis_db)  # connect to server

    def login(self):
        """ Authenticate against the discovergy backend. """

        self.d.login(email, password)

    def update_redis(self):
        """ Populate the redis database with certain discovergy data from the
        past.
        :return: An error if something went wrong, None otherwise
        :rtype: util.error.Error if something went wrong, type(None) otherwise
        """

        # Connect to sqlite database
        session = create_session()

        try:
            # Authenticate against the discovergy backend
            self.login()

        except Exception as e:
            message = exception_message(e)
            logger.error(message)
            logger.error('Wrong or missing discovergy credentials')
            return

        for meter_id in get_all_user_meter_ids(session):
            try:

                # Get the energy consumption for all meters in the ongoing term
                # (start date and end date) and the previous term (start date
                # and end date)
                for timestamp in calculate_timestamps():
                    end_of_day = round((datetime.utcfromtimestamp(
                        timestamp/1000) + timedelta(hours=24, minutes=59,
                                                    seconds=59)).timestamp() * 1000)
                    readings = self.d.get_readings(meter_id, timestamp,
                                                   end_of_day, 'one_hour')

                    if readings == []:
                        logger.info('No readings available for metering id %s',
                                    meter_id)
                        continue

                    for reading in readings:
                        timestamp = reading['time']

                        # Convert unix epoch time in milliseconds to UTC format
                        new_timestamp = datetime.utcfromtimestamp(
                            timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

                        key = meter_id + '_' + str(new_timestamp)

                        # Write reading to redis database as key-value-pair
                        data = dict(type='reading', values=reading['values'])
                        self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)


def run():
    """ Runs the task which fills the redis table with the historical readings. """

    task = Task()
    task.update_redis()


if __name__ == '__main__':
    run()
