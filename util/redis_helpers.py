def get_sorted_keys(redis_client, meter_id):
    """ Return all keys stored in the redis database for a given meter id.
    :param str meter_id: the meter id to prefix the scan with
    """

    return sorted([key.decode('utf-8') for key in
                   redis_client.scan_iter(meter_id + '*')])


def get_sorted_keys_date_prefix(redis_client, meter_id, date):
    """ Return all keys stored in the redis database for a given meter id with
    the given date prefix.
    :param str meter_id: the meter id to prefix the scan with
    :param str date: the date prefix
    """

    return sorted([key.decode('utf-8') for key in
                   redis_client.scan_iter(meter_id + '_' + date + '*')])
