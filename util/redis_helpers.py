def get_sorted_keys(redis_client, meter_id):
    """ Return all keys stored in the redis database for a given meter id.
    :param str meter_id: the meter id to prefix the scan with
    """

    return sorted([key.decode('utf-8') for key in
                   redis_client.scan_iter(meter_id + '*')])
