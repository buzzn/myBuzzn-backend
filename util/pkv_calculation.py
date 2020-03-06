from datetime import datetime, time, timedelta
import json
import logging
import os
from dateutil import parser
import redis
import pytz
from util.database import get_engine
from util.energy_saving_calculation import get_last_meter_reading_date
from util.error import exception_message
from util.redis_helpers import get_sorted_keys


# logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s: %(message)s')
logger.setLevel(logging.DEBUG)

# replace with whatever logfile you see fit for production
logfile = '/tmp/task_worker.log'
filehandler = logging.FileHandler(filename=logfile)
filehandler.setFormatter(formatter)
filehandler.setLevel(logging.ERROR)

# console handler
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)

logger.addHandler(filehandler)
logger.addHandler(streamhandler)

redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def check_input_parameter_date(date):
    """ Check if date does not lie in the future.
    :param datetime.date date: the date to be checked
    :return: True if date does not lie in the future, False otherwise
    """

    today = datetime.utcnow().date()
    if date > today:
        return False
    return True


def get_data_day_before(date, meter_id):
    """ Get the values from the day before from the SQLite database.
    :param datetime.date: the request date
    :param str meter_id: the user's meter id
    :return: date, meter_id, consumption, consumption_cumulated, inhabitants,
    pkv, pkv_cumulated, days, moving_average and moving_average_annualized
    """

    day_before = date - timedelta(days=1)
    day_before_str = str(day_before) + ' 00:00:00.000000'

    try:
        # Connect to sqlite database
        engine = get_engine()
        with engine.connect() as con:

            # pylint: disable=fixme
            # TODO - use SQLAlchemy queries
            # pylint: disable=line-too-long
            query_str = (
                "SELECT * FROM PKV WHERE meter_id = '%s' AND date = '%s'" %
                (meter_id, day_before_str))

            result = con.execute(query_str).first()
            return result

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None


def get_first_meter_reading_date(meter_id, date):
    """ Return the first reading for the given meter id on the given day which
    is stored in the redis database. As we were using unix timestamps as
    basis for our dates all along, there is no need to convert the given,
    timezone-unaware date to UTC.
    : param str meter_id: the meter id for which to get the value
    : param datetime.date date: the date for which to get the value
    : return: the last reading for the given meter id on the given date or
    None if there are no values
    : rtype: float or type(None)
    """

    readings = []
    data = None
    naive_begin = datetime.combine(date, time(0, 0, 0))
    naive_end = datetime.combine(date, time(23, 59, 59))
    timezone = pytz.timezone('UTC')
    begin = (timezone.localize(naive_begin)).timestamp()
    end = (timezone.localize(naive_end)).timestamp()

    for key in get_sorted_keys(redis_client, meter_id):
        try:
            data = json.loads(redis_client.get(key))

        except Exception as e:
            message = exception_message(e)
            logger.error(message)

        if data is not None and data.get('type') == 'reading':
            reading_date = parser.parse(key[len(meter_id)+1:])
            reading_timestamp = reading_date.timestamp()
            if begin <= reading_timestamp <= end:
                readings.append(data.get('values')['energy'])

    if len(readings) > 0:
        return readings[0]

    logger.info('No first reading available for meter id %s on %s',
                meter_id, str(date))
    return None


def define_base_values(inhabitants, date):
    """ Define the base values for a user on a given date.
    :param int inhabitants: the number of inhabitants in the user's flat
    :param datetime.date date: the start date of the calculation which cannot
    lie in the future
    :return: the base values for the given meter id and date or None on wrong
    date parameter
    :rtype: dict or type(None)
    """

    # Check input parameter date
    if check_input_parameter_date(date) is False:
        logger.info(
            'The start date of the calculation cannot lie in the future.')
        return None

    # Define day_zero := Berechnungsstart - 1 Tag
    day_zero = date - timedelta(days=1)

    # Define consumption := 0
    consumption = 0.0

    # On day_zero, consumption_cumulated := consumption (kWh)
    consumption_cumulated = consumption

    # Calculate pkv (Pro-Kopf-Verbrauch) := consumption/inhabitants (kwH)
    pkv = consumption/inhabitants

    # On day_zero, pkv_cumulated := pkv (kWh)
    pkv_cumulated = pkv

    # Define days (since calculation start) := 0 (number)
    days = 0

    # Define moving_average on day_zero := 0.0 (kWh)
    moving_average = 0.0

    # Calculate moving_average_annualized := moving_average * 365 (kWh, rounded)
    moving_average_annualized = round(moving_average * 365)

    # Return base values as dict
    base_values = dict(date=day_zero,
                       consumption=consumption,
                       consumption_cumulated=consumption_cumulated,
                       inhabitants=inhabitants,
                       pkv=pkv,
                       pkv_cumulated=pkv_cumulated,
                       days=days,
                       moving_average=moving_average,
                       moving_average_annualized=moving_average_annualized)
    return base_values


def calc_pkv(meter_id, inhabitants, date):
    """ Calculate the Pro-Kopf-Verbrauch for a given user on a given date.
    :param str meter_id: the user's meter id
    :param int inhabitants: the number of inhabitants in the user's flat
    :param datetime.date date: the calculation day which cannot lie in the future
    :return: the pkv values for the given meter id and date or None if there is
    an error
    :rtype: dict or type(None)
    """

    # Check input parameter date
    if check_input_parameter_date(date) is False:
        logger.info(
            'The input parameter \'date\' cannot lie in the future.')
        return None

    # Calculate consumption := last meter reading of date - first meter reading
    # of date in kWh
    consumption_mywh_last = get_last_meter_reading_date(meter_id, date)
    consumption_mywh_first = get_first_meter_reading_date(meter_id, date)

    if consumption_mywh_last is None or consumption_mywh_first is None:
        return None

    consumption = (consumption_mywh_last - consumption_mywh_first)/1e9

    # Retrieve data for the day before from the SQLite database
    data_day_before = get_data_day_before(date, meter_id)

    if data_day_before is None:
        logger.info(
            'There is no data for the day before %s in the database for meter_id\
                            %s.', date, meter_id)
        return None

    try:
        # Calculate consumption_cumulated := consumption_cumulated of the day
        # before + consumption (kWh)
        consumption_cumulated = data_day_before[2] + consumption

        # Calculate pkv (Pro-Kopf-Verbrauch) := consumption/inhabitants (kWh)
        pkv = consumption/inhabitants

        # Calculate pkv_cumulated := pkv_cumulated of the day
        # before + pkv (kWh)
        pkv_cumulated = data_day_before[6] + pkv

        # Calculate days (since calculation start) := days of the day before + 1
        # (number)
        days = data_day_before[7] + 1

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None

    # Calculate moving_average := pkv_cumulated/days (kWh)
    moving_average = pkv_cumulated/days

    # Calculate moving_average_annualized := moving_average * 365 (kWh, rounded)
    moving_average_annualized = round(moving_average * 365)

    # Return base values as dict
    pkv = dict(date=date,
               consumption=consumption,
               consumption_cumulated=consumption_cumulated,
               inhabitants=inhabitants,
               pkv=pkv,
               pkv_cumulated=pkv_cumulated,
               days=days,
               moving_average=moving_average,
               moving_average_annualized=moving_average_annualized
               )
    return pkv