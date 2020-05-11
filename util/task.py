import json
import os
import math
from os import path
import time as stdlib_time
from datetime import datetime, timedelta
import logging.config
from discovergy.discovergy import Discovergy
import redis
from util.error import exception_message
from util.database import create_session
from util.date_helpers import calc_support_year_start, calc_term_boundaries,\
    calc_end, calc_support_week_start, calc_two_days_back
from util.sqlite_helpers import get_all_meter_ids, write_baselines,\
    write_savings, write_base_values_or_per_capita_consumption
from util.redis_helpers import get_keys_date_hour_prefix, get_entry_date


log_file_path = path.join(path.dirname(
    path.abspath(__file__)), 'logger_configuration.conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
client_name = 'BuzznClient'
email = os.environ['DISCOVERGY_EMAIL']
password = os.environ['DISCOVERGY_PASSWORD']
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
last_data_flush = None
end_next_interval = None


def check_and_nullify_power_value(reading, meter_id):
    """ Sometimes discovergy delivers a negative power value; set it to 0.
    :param dict reading: a single reading obtained from discovergy
    :param str meter_id: the meter id the reading belongs to
    :return: the adjusted reading
    :rtype: dict
    """

    if 'power' in reading['values'].keys() and reading['values']['power'] < 0:
        message = 'Received negative power value {} from Discovergy for meter id {}'.format(
            reading['values']['power'], meter_id)
        logger.warning(message)
        reading['values']['power'] = 0
    return reading


class Task:
    """ Handle discovergy login, data retrieval, populating and updating the
    redis database. """

    def __init__(self):
        self.d = Discovergy(client_name)
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)  # connect to server

        # pylint: disable=global-statement
        global end_next_interval
        # set end_next_interval to end of next quarter-hour
        current_time = datetime.utcnow()
        nsecs = current_time.minute * 60 + current_time.second + \
                current_time.microsecond * 1e-6
        delta = math.ceil(nsecs / 900) * 900 - nsecs
        end_next_interval = current_time + timedelta(seconds=delta)


    def login(self):
        """ Authenticate against the discovergy backend. """

        self.d.login(email, password)

    def write_readings(self, session, end):
        """ Get all readings for all meters from one the beginning of the BAFA support
        year until now with one-week interval (this is the finest granularity we get for one
        year back in time, cf. https://api.discovergy.com/docs/) and write them
        to the redis database.
        :param sqlalchemy.orm.scoping.scoped_session session: the database session
        :param int end: end of interval in the format required by the
        discovergy API
        """

        for meter_id in get_all_meter_ids(session):

            try:
                readings = self.d.get_readings(meter_id,
                                               calc_support_year_start(), end,
                                               'one_week')

                if readings == []:
                    message = 'No readings available for metering id {}'.format(
                        meter_id)
                    logger.info(message)
                    continue

                for reading in readings:
                    adjusted_reading = check_and_nullify_power_value(reading,
                                                                     meter_id)
                    timestamp = adjusted_reading['time']

                    # Convert unix epoch time in milliseconds to UTC format
                    new_timestamp = datetime.utcfromtimestamp(timestamp/1000).\
                        strftime('%Y-%m-%d %H:%M:%S')

                    key = meter_id + '_' + str(new_timestamp)

                    # Write adjusted reading to redis database as key-value-pair
                    # The unique key consists of the meter id (16 chars), the
                    # separator '_' and the UTC timestamp (19 chars)
                    data = dict(type='reading',
                                values=adjusted_reading['values'])
                    self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)

    def write_last_readings(self, session):
        """ Get the last reading for all meters and write them to the redis
        database.
        :param sqlalchemy.orm.scoping.scoped_session session: the database session
        """

        for meter_id in get_all_meter_ids(session):

            try:
                reading = self.d.get_last_reading(meter_id)
                if reading == {}:
                    message = 'No last reading available for metering id {}'.format(
                        meter_id)
                    logger.info(message)
                    continue

                adjusted_reading = check_and_nullify_power_value(
                    reading, meter_id)
                reading_timestamp = str(datetime.utcfromtimestamp(
                    adjusted_reading['time']/1000).strftime('%F %T'))
                key = meter_id + '_' + reading_timestamp
                date_key = datetime.utcnow().strftime('%Y-%m-%d')
                # Write reading to redis database as key-value-pair
                # The unique key consists meter id, separator '_' and UTC
                # timestamp
                data = dict(type='reading', values=adjusted_reading['values'])
                self.redis_client.set(key, json.dumps(data))
                self.redis_client.set(meter_id + '_last', json.dumps(data))
                data["time"] = reading_timestamp
                self.redis_client.set(meter_id + '_' + date_key + '_last', json.dumps(data))

                if self.redis_client.get(meter_id + '_' + date_key + '_first') is None:
                    self.redis_client.set(meter_id + '_' + date_key + '_first', json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)

    def write_energy_consumption(self, session):
        """ Get readings for all meters at start and end dates of
        previous and ongoing terms and write them to the redis database.
        :param sqlalchemy.orm.scoping.scoped_session session: the database session
        """

        for meter_id in get_all_meter_ids(session):

            try:
                for timestamp in calc_term_boundaries():
                    end_of_day = round((datetime.utcfromtimestamp(
                        timestamp/1000) + timedelta(hours=24, minutes=59,
                                                    seconds=59)).timestamp() * 1000)

                    readings = self.d.get_readings(meter_id, timestamp,
                                                   end_of_day, 'one_hour')

                    if readings == []:
                        message = 'No readings available for metering id {}'.format(
                            meter_id)
                        logger.info(message)
                        continue

                    for reading in readings:
                        adjusted_reading = check_and_nullify_power_value(
                            reading, meter_id)
                        timestamp = adjusted_reading['time']

                        # Convert unix epoch time in milliseconds to UTC format
                        new_timestamp = datetime.utcfromtimestamp(
                            timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

                        key = meter_id + '_' + str(new_timestamp)

                        # Write adjusted reading to redis database as key-value-pair
                        data = dict(type='reading',
                                    values=adjusted_reading['values'])
                        self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)

    def write_disaggregations(self, session, end):
        """ Get all disaggregation values for all meters from one week back
        until now. This is the earliest data we get, otherwise you'll end up
        with a '400 Bad Request: Duration of the data cannot be larger than 1
        week. Please try for a smaller duration.' If one week back lies before
        the current BAFA support year start, start with that value instead.
        :param sqlalchemy.orm.scoping.scoped_session session: the database session
        :param int end: end of interval in the format required by the
        discovergy API
        """

        for meter_id in get_all_meter_ids(session):

            try:

                disaggregation = self.d.get_disaggregation(
                    meter_id, calc_support_week_start(), end)

                if disaggregation == {}:
                    message = 'No disaggregation available for metering id {}'.format(
                        meter_id)
                    logger.info(message)
                    continue

                for timestamp in disaggregation:

                    # Convert unix epoch time in milliseconds to UTC format
                    new_timestamp = datetime.utcfromtimestamp(
                        int(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')
                    key = meter_id + '_' + str(new_timestamp)

                    # Write disaggregation to redis database as key-value-pair
                    # The unique key consists of meter id, separator '_' and UTC timestamp
                    data = dict(type='disaggregation',
                                values=disaggregation[timestamp])
                    self.redis_client.set(meter_id + '_last_disaggregation', json.dumps(data))
                    self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)

    def write_last_disaggregations(self, session):
        """ Get the last disaggregation values for all meters and write them to the redis
        database.
        :param sqlalchemy.orm.scoping.scoped_session session: the database session
        """

        two_days_back = calc_two_days_back()
        for meter_id in get_all_meter_ids(session):

            try:
                disaggregation = self.d.get_disaggregation(
                    meter_id, two_days_back, calc_end())

                if disaggregation in ({}, []):
                    message = 'No disaggregation available for metering id {}'.format(
                        meter_id)
                    logger.info(message)
                    continue

                timestamps = sorted(disaggregation.keys())
                if len(timestamps) > 0:
                    timestamp = timestamps[-1]

                    # Convert unix epoch time in milliseconds to UTC format
                    new_timestamp = datetime.utcfromtimestamp(int(timestamp)/1000).\
                        strftime('%Y-%m-%d %H:%M:%S')

                    key = meter_id + '_' + str(new_timestamp)

                    # Write disaggregation to redis database as key-value-pair
                    # The unique key consists of meter id (16 chars), separator '_' and UTC
                    # timestamp
                    data = dict(type='disaggregation',
                                values=disaggregation[timestamp])

                    self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)

    def calculate_average_power(self, session):
        # pylint: disable=global-statement
        global end_next_interval
        date_interval = (end_next_interval - timedelta(minutes=15)).strftime("%Y-%m-%d")
        hour_interval = (end_next_interval - timedelta(minutes=15)).strftime("%H")

        for meter_id in get_all_meter_ids(session):
            average_power_key = 'average_power_' + meter_id + '_' + date_interval
            power_sum = 0
            divider = 0
            for key in get_keys_date_hour_prefix(self.redis_client, meter_id, date_interval,
                                                 hour_interval):

                reading_date, data = get_entry_date(self.redis_client, meter_id, key, 'reading')

                if reading_date is None:
                    continue

                reading_timestamp = reading_date.timestamp()

                if ((end_next_interval - timedelta(minutes=15)).timestamp() < reading_timestamp
                        <= end_next_interval.timestamp()):
                    power_sum += data.get('values').get('power')
                    divider += 1

            if divider != 0:
                average = power_sum / divider
            else:
                average = 0
                message = f"No readings available for {meter_id} between " \
                          f"{(end_next_interval - timedelta(minutes=15))} and {end_next_interval}"
                logger.info(message)

            if len(self.redis_client.keys(average_power_key)) == 0:
                data = {end_next_interval.strftime("%Y-%m-%d %H:%M:%S"): average}

            else:
                data = json.loads(self.redis_client.get(average_power_key))
                data[end_next_interval.strftime("%Y-%m-%d %H:%M:%S")] = average

            self.redis_client.set(average_power_key, json.dumps(data))
            self.redis_client.expire(average_power_key, int(timedelta(days=3).total_seconds()))

    def populate_redis(self):
        """ Populate the redis database with all discovergy data from the past. """

        # pylint: disable=global-statement
        global last_data_flush
        last_data_flush = datetime.utcnow()
        end = calc_end()

        # Connect to sqlite database
        session = create_session()

        try:
            # Authenticate against the discovergy backend
            self.login()

        except Exception as e:
            message = exception_message(e)
            logger.error(message)
            logger.error('Wrong or missing discovergy credentials.')
            return

        self.write_readings(session, end)
        self.write_energy_consumption(session)
        self.write_disaggregations(session, end)

    def update_redis(self):
        """ Update the redis database every 60s with the latest discovergy data. """

        message = 'Started redis task at {}'.format(
            datetime.now().strftime("%H:%M:%S"))
        logger.info(message)

        while True:
            stdlib_time.sleep(60)
            message = 'Fill redis at {}'.format(
                datetime.now().strftime("%H:%M:%S"))
            logger.info(message)

            # Populate redis if last data flush was more than 24h ago
            # pylint: disable=global-statement
            global last_data_flush
            global end_next_interval

            # Connect to SQLite database
            session = create_session()

            if (last_data_flush is None) or (datetime.utcnow() -
                                             last_data_flush >
                                             timedelta(hours=24)):
                self.populate_redis()
                write_baselines(session)
                write_savings(session)
                write_base_values_or_per_capita_consumption(session)

            self.write_last_readings(session)
            self.write_last_disaggregations(session)

            if (datetime.utcnow() - end_next_interval) > timedelta(0):
                self.calculate_average_power(session)
                end_next_interval = end_next_interval + timedelta(minutes=15)


def run():
    """ Runs the task which fills the redis database with the latest readings. """

    task = Task()
    task.update_redis()


if __name__ == '__main__':
    run()
