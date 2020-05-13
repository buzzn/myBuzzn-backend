import os
from datetime import datetime
import redis
from util.redis_helpers import get_entry_date


redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_readings(meter_id, begin):
    """ Return all readings for the given meter id, starting with the given
    timestamp. As we were using unix timestamps as basis for our dates all
    along, there is no need to convert the given, timezone-unaware dates to UTC.
    :param str meter_id: the meter id for which to get the values
    :param int begin: the unix timestamp to begin with
    """

    result = {}
    all_keys = sorted([key.decode('utf-8')
                       for key in redis_client.scan_iter(meter_id + '*')])
    for key in all_keys:

        reading_date, data = get_entry_date(redis_client, meter_id, key, 'reading')

        if reading_date is None or data is None:
            continue

        reading_timestamp = reading_date.timestamp()
        if reading_timestamp >= begin:
            result[reading_date.strftime('%Y-%d-%m %H:%S:%M')] = data.get('values')

    return result


if __name__ == '__main__':
    mid = 'b4234cd4bed143a6b9bd09e347e17d34'
    b = datetime.combine(
        datetime.utcnow(), datetime.min.time()).timestamp()
    readings = get_readings(mid, b)
    print(readings)
