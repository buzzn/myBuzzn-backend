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
    else:
        if data is not None and data.get('type') == entry_type:
            entry_date = parser.parse(key[len(meter_id) + 1:])
            return entry_date, data

    return None, None


# pylint: disable=too-many-locals
def get_first_meter_reading_date(redis_client, meter_id, date):
    """ Return the first reading for the given meter id on the given day which
    is stored in the redis database. As we were using unix timestamps as
    basis for our dates all along, there is no need to convert the stored,
    timezone-unaware date to UTC.
    : param str meter_id: the meter id for which to get the value
    : param str date: the date for which to get the value
    : returns: the last reading for the given meter id on the given date or
    None if there are no values
    : rtype: float or type(None)
    """
    key_date_first = f"{meter_id}_{date}_first"
    redis_key_date_first = redis_client.get(key_date_first)

    if redis_key_date_first is None:
        logger.info("No key %s_%s_first available. Iteration needed.", meter_id, date)
        sorted_keys_date = get_sorted_keys_date_prefix(redis_client, meter_id, date)

        if len(sorted_keys_date) == 0:
            logger.info('No first reading available for meter id %s on %s', meter_id, str(date))
            return None

        for key in sorted_keys_date:
            reading_date, data = get_entry_date(redis_client, meter_id, key, 'reading')

            if reading_date is None or data is None:
                continue

            data["time"] = reading_date.timestamp()
            redis_client.set(key_date_first, json.dumps(data))
            return data.get('values').get('energy')

    try:
        data = json.loads(redis_key_date_first)

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
    else:
        return data.get('values').get('energy')


# pylint: disable=too-many-locals
def get_last_meter_reading_date(redis_client, meter_id, date):
    """ Return the first reading for the given meter id on the given day which
    is stored in the redis database. As we were using unix timestamps as
    basis for our dates all along, there is no need to convert the stored,
    timezone-unaware date to UTC.
    : param str meter_id: the meter id for which to get the value
    : param str date: the date for which to get the value
    : returns: the last reading for the given meter id on the given date or
    None if there are no values
    : rtype: float or type(None)
    """
    key_date_last = f"{meter_id}_{date}_last"
    redis_key_date_last = redis_client.get(key_date_last)

    if redis_key_date_last is None:
        logger.info("No key %s_%s_last available. Iteration needed.", meter_id, date)
        sorted_keys_date = get_sorted_keys_date_prefix(redis_client, meter_id, date)

        if len(sorted_keys_date) == 0:
            logger.info('No last reading available for meter id %s on %s', meter_id, str(date))
            return None

        for key in reversed(sorted_keys_date):
            reading_date, data = get_entry_date(redis_client, meter_id, key, 'reading')

            if reading_date is None or data is None:
                continue

            data["time"] = reading_date.timestamp()
            redis_client.set(key_date_last, json.dumps(data))
            return data.get('values').get('energy')

    try:
        data = json.loads(redis_key_date_last)

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
    else:
        return data.get('values').get('energy')
