from datetime import datetime, timedelta
import logging
import os
import redis
from util.energy_saving_calculation import get_meter_reading_date


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


def define_base_values(meter_id, inhabitants, date):
    """ Create the base values for the user with the given meter id for the
    given date.
    :param str meter_id: the user's meter id
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

    # Calculate consumption := last meter reading of the day before calculation
    # start (kWh)
    consumption_mywh = get_meter_reading_date(meter_id, day_zero)
    if consumption_mywh is None:
        return None
    consumption = consumption_mywh/1e9

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
    :return: the pkv values for the given meter id and date or None on wrong
    date parameter
    :rtype: dict or type(None)
    """

    # Check input parameter date
    if check_input_parameter_date(date) is False:
        logger.info(
            'The input parameter \'date\' cannot lie in the future.')
        return None

    # Calculate consumption := last meter reading of date in kWh
    consumption_mywh = get_meter_reading_date(meter_id, date)
    if consumption_mywh is None:
        return None
    consumption = consumption_mywh/1e9

    # pylint: disable=fixme
    # TODO
    # Calculate consumption_cumulated := consumption_cumulated of the day
    # before + consumption (kWh)

    # Calculate pkv (Pro-Kopf-Verbrauch) := consumption/inhabitants (kWh)
    pkv = consumption/inhabitants

    # TODO
    # Calculate pkv_cumulated := pkv_cumulated := pkv_cumulated of the day
    # before + pkv (kWh)

    # TODO
    # Calculate days (since calculation start) := days of the day before + 1
    # (number)

    # TODO
    # Calculate moving_average := pkv_cumulated/days (kWh)

    # Calculate moving_average_annualized := moving_average * 365 (kWh, rounded)

    # Return base values as dict
    pkv = dict(date=date,
               consumption=consumption,
               # consumption_cumulated=consumption_cumulated,
               inhabitants=inhabitants,
               pkv=pkv,
               # pkv_cumulated=pkv_cumulated,
               # days=days,
               # moving_average=moving_average,
               # moving_average_annualized=moving_average_annualized
               )
    return pkv
