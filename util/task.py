import json
import os
from os import path
import time as stdlib_time
from datetime import datetime, timedelta, date, time
import logging.config
from discovergy.discovergy import Discovergy
import redis
from models.baseline import BaseLine
from models.user import User
from models.group import Group
from models.pkv import PKV
from models.savings import UserSaving, CommunitySaving
from util.error import exception_message
from util.energy_saving_calculation import estimate_energy_saving_each_user,\
    estimate_energy_saving_all_users, get_all_user_meter_ids, calc_energy_consumption_last_term
from util.database import create_session
from util.pkv_calculation import define_base_values, calc_pkv


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
message_timestamp = datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S')


def get_all_meter_ids(session):
    """ Get all meter ids from the SQLite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]\
        + [group_meter_id[0]
           for group_meter_id in session.query(Group.group_meter_id).all()]\
        + [group_production_meter_id_first[0] for
           group_production_meter_id_first in
           session.query(Group.group_production_meter_id_first).all()]\
        + [group_production_meter_id_second[0] for group_production_meter_id_second
           in session.query(Group.group_production_meter_id_second).all()]


def get_all_users(session):
    """ Get all users from the SQLite database. """

    return session.query(User).all()


def calc_term_boundaries():
    """ Calculate begin and end of previous and ongoing terms.
    :return: begin and end of the previous and the current support year until
    today as unix milliseconds timestamps
    :rtype: tuple(int)
    """

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


def calc_end():
    """ Calculate timestamp of end of interval. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round(datetime.utcnow().timestamp() * 1000)


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


def calc_support_year_start_datetime():
    """ Calculate start of BAFA support year.
    :return:
    March, 12th the year before if today is between January, 1st and March, 11th
    March, 12th of the current year otherwise
    :rtype: datetime.date in UTC
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
    return datetime.combine(d, t)


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


def calc_two_days_back():
    """ Calculate timestamp of 48 hours back in time. """

    # Multiply the result of timestamp() from the standard library by 1000 and
    # round it to have no decimal places to match the timestamp format required
    # by the discovergy API
    return round((datetime.utcnow() - timedelta(hours=48)).timestamp() * 1000)


def write_savings(session):
    """ Write the energy savings of each user and the community to the
    SQLite database.
    """

    start = calc_support_year_start_datetime()
    try:
        for key, value in estimate_energy_saving_each_user(start,
                                                           session).items():

            if value is None:
                message = """Cannot calculate saving for meter id {} on {}
                because last term\'s energy consumption or estimated energy
                consumption is missing. Writing 0.0 instead""".format(key,
                                                                      message_timestamp)
                logger.info(message)

                # Create UserSaving instance and set saving to 0.0
                user_saving = UserSaving(datetime.utcnow(), key, 0.0)

            else:
                user_saving = UserSaving(datetime.utcnow(), key, value)

            session.add(user_saving)

        # Create CommunitySaving instance
        community_saving = estimate_energy_saving_all_users(start, session)
        session.add(CommunitySaving(datetime.utcnow(), community_saving))

        session.commit()
    except Exception as e:
        message = exception_message(e)
        logger.error(message)


def write_baselines(session):
    """ Write the baseline for each user to the SQLite database. """

    start = calc_support_year_start_datetime()
    try:
        for meter_id in get_all_user_meter_ids(session):
            baseline = calc_energy_consumption_last_term(meter_id, start)

            if baseline is None:
                message = """Cannot write baseline for meter id {} on {} because last term\'s energy
                consumption is missing""".format(meter_id, message_timestamp)
                logger.info(message)

            else:
                # Create BaseLine instance
                session.add(BaseLine(datetime.utcnow(), meter_id, baseline))

        session.commit()
    except Exception as e:
        message = exception_message(e)
        logger.error(message)


def write_base_values_or_pkv(session):
    """ If yesterday was the start of the support year, write the base values
    for all users to the SQLite database.
    Otherwise, write yesterday's pkv for all users to the SQLite database.
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    """

    yesterday_date = (datetime.today() - timedelta(days=1)).date()
    today_date = datetime.today().date()
    _time = time(0, 0, 0)
    yesterday = datetime.combine(yesterday_date, _time)
    today = datetime.combine(today_date, _time)
    support_year_start = calc_support_year_start_datetime()

    if today == support_year_start:
        write_base_values(yesterday, session)
    else:
        write_pkv(yesterday, session)


def write_base_values(dt, session):
    """ Write the base values for each user to the SQLite database.
    :param datetime dt: the date to write the values for
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    """

    for user in get_all_users(session):
        base_values = define_base_values(user.inhabitants, dt)

        # Create PKV instance
        session.add(PKV(dt, user.meter_id, base_values['consumption'],
                        base_values['consumption_cumulated'],
                        base_values['inhabitants'], base_values['pkv'],
                        base_values['pkv_cumulated'], base_values['days'],
                        base_values['moving_average'],
                        base_values['moving_average_annualized']))

    session.commit()


def write_pkv(dt, session):
    """ Write the pkv for each user to the SQLite database.
    If for one user there are no yesterday's values in the database, write the
    base values for that user.
    If today's entry already exists for a user, skip writing that entry.
    :param datetime dt: the date to write the values for
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    """

    for user in get_all_users(session):

        try:
            # Check if entry exists
            pkv_today = session.query(PKV).filter_by(
                date=dt, meter_id=user.meter_id).first()

            # Create today's entry if it does not exist
            if not pkv_today:
                dataset = calc_pkv(
                    user.meter_id, user.inhabitants, dt, session)

                # If there are no yesterday's values in the database for this user,
                # define the base values
                if dataset is None:
                    dataset = define_base_values(user.inhabitants, dt)

            # Create PKV instance
                session.add(PKV(dt, user.meter_id, dataset['consumption'],
                                dataset['consumption_cumulated'],
                                dataset['inhabitants'], dataset['pkv'],
                                dataset['pkv_cumulated'], dataset['days'],
                                dataset['moving_average'],
                                dataset['moving_average_annualized']))
        except Exception as e:
            message = exception_message(e)
            logger.error(message)

    session.commit()


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

        for meter_id in get_all_meter_ids(session):
            try:
                # Get all readings for all meters from one the beginning of the
                # BAFA support year until now with
                # one-week interval (this is the finest granularity we get for one
                # year back in time, cf. https://api.discovergy.com/docs/)
                readings = self.d.get_readings(meter_id,
                                               calc_support_year_start(), end,
                                               'one_week')

                if readings == []:
                    message = 'No readings available for metering id {}'.format(
                        meter_id)
                    logger.info(message)
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

                # Get the energy consumption for all meters in the ongoing term
                # (start date and end date) and the previous term (start date
                # and end date)
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
                        timestamp = reading['time']

                        # Convert unix epoch time in milliseconds to UTC format
                        new_timestamp = datetime.utcfromtimestamp(
                            timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

                        key = meter_id + '_' + str(new_timestamp)

                        # Write reading to redis database as key-value-pair
                        data = dict(type='reading', values=reading['values'])
                        self.redis_client.set(key, json.dumps(data))

                # Get all disaggregation values for all meters from one week back
                # until now. This is the earliest data we get, otherwise you'll
                # end up with a '400 Bad Request: Duration of the data
                # cannot be larger than 1 week. Please try for a smaller duration.'
                # If one week back lies before the current BAFA support year
                # start, start with that value instead.
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
                    # The unique key consists of the meter id (16 chars), the
                    # separator '_' and the UTC timestamp (19 chars)
                    data = dict(type='disaggregation',
                                values=disaggregation[timestamp])
                    self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)

    def update_redis(self):
        """ Update the redis database every 60s with the latest discovergy
        data. """

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

            # Connect to SQLite database
            session = create_session()

            if (last_data_flush is None) or (datetime.utcnow() -
                                             last_data_flush >
                                             timedelta(hours=24)):
                self.populate_redis()
                write_baselines(session)
                write_savings(session)
                write_base_values_or_pkv(session)

            try:
                all_meter_ids = get_all_meter_ids(session)
                end = calc_end()
                two_days_back = calc_two_days_back()

                # Get last reading for all meters
                for meter_id in all_meter_ids:
                    reading = self.d.get_last_reading(meter_id)

                    if reading == {}:
                        message = 'No last reading available for metering id {}'.format(
                            meter_id)
                        logger.info(message)
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
                        # The unique key consists of the meter id (16 chars), the
                        # separator '_' and the UTC timestamp (19 chars)
                        data = dict(type='disaggregation',
                                    values=disaggregation[timestamp])
                        self.redis_client.set(key, json.dumps(data))

            except Exception as e:
                message = exception_message(e)
                logger.error(message)


def run():
    """ Runs the task which fills the redis database with the latest readings. """

    task = Task()
    task.update_redis()


if __name__ == '__main__':
    run()
