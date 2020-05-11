import json
import logging.config
from dateutil import parser
from util.error import exception_message

logger = logging.getLogger(__name__)


def get_sorted_keys(redis_client, meter_id):
    """ Return all keys stored in the redis database for a given meter id.
    :param str meter_id: the meter id to prefix the scan with
    """

    return sorted([key.decode('utf-8') for key in
                   redis_client.scan_iter(meter_id + '*', 200)])


def get_sorted_keys_date_prefix(redis_client, meter_id, date):
    """ Return all keys stored in the redis database for a given meter id with
    the given date prefix.
    :param str meter_id: the meter id to prefix the scan with
    :param str date: the date prefix
    """

    return sorted([key.decode('utf-8') for key in
                   redis_client.scan_iter(meter_id + '_' + date + '*', 200)])


def get_keys_date_hour_prefix(redis_client, meter_id, date, hour):
    """ Return all keys in the redis database for a given meter id with
    the given date and hour  prefix.
    :param str meter_id: the meter id to prefix the scan with
    :param str date: the date prefix
    :param str hour: the hour prefix
    """
    return [key.decode('utf-8') for key in
            redis_client.scan_iter(meter_id + '_' + date + ' ' + hour + '*')]


def get_entry_date(redis_client, meter_id, key, entry_type):
    """ Return creation date of an entry in the redis database.
    :param str meter_id: the meter id the entry belongs to
    :param str key: the entry's key
    :param str entry_type: the entry's type (reading or disaggregation)
    """
    if (key[len(meter_id) + 1:].endswith("last")
            or key[len(meter_id) + 1:].endswith("first")
            or key[len(meter_id) + 1:].endswith("last_disaggregation")
            or key.startswith('average_power')):
        return None, None

    try:
        data = json.loads(redis_client.get(key))

    except Exception as e:
        message = exception_message(e)
        logger.error(message)

    if data is not None and data.get('type') == entry_type:
        entry_date = parser.parse(key[len(meter_id) + 1:])
        return entry_date, data

    return None, None
