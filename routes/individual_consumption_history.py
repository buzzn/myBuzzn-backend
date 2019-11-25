import os
from datetime import datetime
import logging
from discovergy.discovergy import Discovergy
from flask import Blueprint, jsonify
from flask import request

_LOGGER = logging.getLogger(__name__)
client_name = 'BuzznClient'


IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)


@IndividualConsumptionHistory.route('/individual-consumption-history')
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval.
    :param str begin: start time of consumption, default is today at 0:00
    :param str end: end time of consumption, default is
    datetime.datetime.now()
    :param str resolution: time distance between returned readings with
    possible values 'raw', 'three_minutes', 'fifteen_minutes', 'one_hour',
    'one_day', 'one_week', 'one_month', 'one_year', default is 'three_minutes'
    :return: (array of float values where each one stands for the total power
    consumed at the time, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    # TODO - Set meter ID in database

    # TODO - Get meter ID from database

    # Use the given parameters
    start = round(datetime.combine(datetime.now(),
                                   datetime.min.time()).timestamp() * 1e3)
    print(type(start))
    begin = request.args.get('begin', default=start, type=int)
    end = request.args.get('end', default=None, type=int)
    tics = request.args.get('tics', default='three_minutes', type=str)

    # Call discovergy API for the given meter
    d = Discovergy(client_name)
    d.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    result = []
    empty_result = {}
    try:
        if end is None:
            readings = d.get_readings(os.environ['METER_ID'], start, None,
                                      'three_minutes')
        else:
            readings = d.get_readings(
                os.environ['METER_ID'], start, end, 'three_minutes')
        for reading in readings:
            result.append(float(reading.get('values').get('power')))

        # Return result
        return jsonify(result), 200

    except TypeError as e:
        _LOGGER.error("Exception: %s", e)

        # Return result
        return empty_result, 206
