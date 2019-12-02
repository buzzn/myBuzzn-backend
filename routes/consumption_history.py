import os
from datetime import datetime

# We want to structure our routes in different modules and therefore use equal
# imports. Likewise, we want the logger in each module for now.
# pylint: disable=duplicate-code
import logging
# pylint: disable=duplicate-code
from flask import Blueprint, jsonify, request
# pylint: disable=duplicate-code
from flask_api import status
# pylint: disable=duplicate-code
from flask import current_app as app
# pylint: disable=duplicate-code
from discovergy.discovergy import Discovergy


# pylint: disable=duplicate-code
logger = logging.getLogger(__name__)
IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)
GroupConsumptionHistory = Blueprint('GroupConsumptionHistory', __name__)


def read_parameters():
    """ Use the given parameters. """

    # Calculate the minimal time of "today", i.e. 00:00 am, as unix timestamp
    # as integer with milliseconds precision. The timestamp format is required
    # by the discovergy API, cf. https://api.discovergy.com/docs/
    start = round(datetime.combine(datetime.now(),
                                   datetime.min.time()).timestamp() * 1e3)
    begin = request.args.get('begin', default=start, type=int)
    end = request.args.get('end', default=None, type=int)
    tics = request.args.get('tics', default='one_hour', type=str)
    return begin, end, tics


@IndividualConsumptionHistory.route('/individual-consumption-history',
                                    methods=['GET'])
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval in mW.
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
    # pylint: disable=fixme
    # TODO - Set meter ID in database
    # TODO - Get meter ID from database

    # Call discovergy API for the given meter
    begin, end, tics = read_parameters()
    client_name = app.config['CLIENT_NAME']
    d = Discovergy(client_name)
    d.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    result = {}
    try:
        readings = d.get_readings(os.environ['METER_ID'], begin, end, tics)
        for reading in readings:
            result[reading.get('time')] = reading.get('values').get('power')

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except ValueError as e:
        logger.error("%s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT


@GroupConsumptionHistory.route('/group-consumption-history', methods=['GET'])
def group_consumption_history():
    """ Shows the history of consumption of the given time interval in mW.
    :param int begin: start time of consumption, default is today at 0:00
    :param int end: end time of consumption, default is $now
    :param str tics: time distance between returned readings with possible
    values 'raw', 'three_minutes', 'fifteen_minutes', 'one_hour', 'one_day',
    'one_week', 'one_month', 'one_year', default is 'one_hour'
    :return: ({"consumed": str => int, "produced": str => int}, 200) or ({},
    206) if there is no history
    :rtype: tuple
    """

    # pylint: disable=fixme
    # TODO - Set group meter ID in database
    # TODO - Get group meter ID from database

    # Call discovergy API for the given group meter
    begin, end, tics = read_parameters()
    client_name = app.config['CLIENT_NAME']
    d = Discovergy(client_name)
    d.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    result = {}
    produced = {}
    consumed = {}

    try:
        readings = d.get_readings(os.environ['GROUP_METER_ID'], begin, end,
                                  tics)
        for reading in readings:
            produced[reading.get('time')] = reading.get(
                'values').get('energyOut')
            consumed[reading.get('time')] = reading.get('values').get('power')

        # Return result
        result["consumed"] = consumed
        result["produced"] = produced
        return jsonify(result), status.HTTP_200_OK

    except TypeError as e:
        logger.error("%s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
