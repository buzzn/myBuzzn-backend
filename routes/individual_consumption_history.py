import os
from datetime import datetime
import logging
from flask import Blueprint, jsonify, request
from discovergy.discovergy import Discovergy


_LOGGER = logging.getLogger(__name__)
client_name = 'BuzznClient'
IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)


@IndividualConsumptionHistory.route('/individual-consumption-history',
                                    methods=['GET'])
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval.
    :param int begin: start time of consumption, default is today at 0:00
    :param int end: end time of consumption, default is
    datetime.datetime.now()
    :param str tics: time distance between returned readings with
    possible values 'raw', 'three_minutes', 'fifteen_minutes', 'one_hour',
    'one_day', 'one_week', 'one_month', 'one_year', default is 'one_hour'
    :return: (a JSON object where each meter reading is mapped to its point
    in time, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    # TODO - Set meter ID in database

    # TODO - Get meter ID from database

    # Use the given parameters
    start = round(datetime.combine(datetime.now(),
                                   datetime.min.time()).timestamp() * 1e3)
    begin = request.args.get('begin', default=start, type=int)
    end = request.args.get('end', default=None, type=int)
    tics = request.args.get('tics', default='one_hour', type=str)

    # Call discovergy API for the given meter
    d = Discovergy(client_name)
    d.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    result = {}
    try:
        readings = d.get_readings(os.environ['METER_ID'], begin, end, tics)
        for reading in readings:
            result[reading.get('time')] = reading.get('values').get('power')

        # Return result
        return jsonify(result), 200

    except TypeError as e:
        _LOGGER.error("Exception: %s", e)

        # Return result
        return jsonify(result), 206
