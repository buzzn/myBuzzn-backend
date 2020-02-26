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


def define_base_values(meter_id, inhabitants, date):
    """ Create the base values for the user with the given meter id for the
    given date.
    :param str meter_id: the user's meter id
    :param int inhabitants: the number of inhabitants in the user's flat
    :param datetime.date date: the start date of the calculation which must lie
    before today's date
    :return: the base values for the given meter id and date or None on wrong
    date parameter
    :rtype: dict or type(None)
    """

    # Check input parameter date
    today = datetime.utcnow().date()
    if date > today:
        logger.info(
            'The start date of the calculation must lie before today\'s date.')
        return None

    day_zero = date - timedelta(days=1)

    consumption = get_meter_reading_date(meter_id, day_zero)
    if consumption is None:
        return None

    # Convert consumption from µWh to kWh
    consumption_kwh = consumption/1e9

    consumption_cumulated = consumption

    pkv = consumption/inhabitants

    pkv_cumulated = pkv

    days = 0

    moving_average = 0

    moving_average_annualized = moving_average * 365

    base_values = dict(date=datetime.strftime(day_zero, '%Y-%m-%d'),
                       consumption=consumption_kwh,
                       consumption_cumulated=consumption_cumulated,
                       inhabitants=inhabitants, pkv=pkv,
                       pkv_cumulated=pkv_cumulated, days=days,
                       moving_average=moving_average,
                       moving_average_annualized=moving_average_annualized)
    return base_values
