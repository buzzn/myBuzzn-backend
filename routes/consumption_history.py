import json
import os
from datetime import datetime
import logging
from dateutil import parser
import redis
from flask import Blueprint, jsonify, request
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.user import User
from util.database import db
from util.error import UNKNOWN_USER, UNKNOWN_GROUP
from util.login import login_required, get_parameters


logger = logging.getLogger(__name__)
IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)
GroupConsumptionHistory = Blueprint('GroupConsumptionHistory', __name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_sorted_keys(meter_id):
    """ Return all keys stored in the redis db for a given meter id.
    :param str meter_id: the meter id to prefix the scan with
    """

    return sorted([key.decode('utf-8') for key in redis_client.scan_iter(meter_id + '*')])


def get_all_readings(meter_id):
    """ Return all readings for the given meter id.
    :param str meter_id: the meter id for which to get the values
    """

    result = {}
    for key in get_sorted_keys(meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'reading':
            timestamp = key[len(meter_id)+1:]
            result[timestamp] = data.get('values')
    return result


def get_readings(meter_id, begin):
    """ Return all readings for the given meter id, starting with the given
    timestamp. As we were using unix timestamps as basis for our dates all
    along, there is no need to convert the given, timezone-oblivious dates to UTC.
    :param str meter_id: the meter id for which to get the values
    :param int begin: the unix timestamp to start with
    """

    result = {}
    for key in get_sorted_keys(meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'reading':
            reading_date = parser.parse(key[len(meter_id)+1:])
            reading_timestamp = reading_date.timestamp()
            if reading_timestamp >= begin:
                result[reading_date.strftime(
                    '%Y-%d-%m %H:%S:%M')] = data.get('values')
    return result


def read_begin_parameter():
    """ Use the given begin parameter. """

    # Calculate the minimal time of "today", i.e. 00:00 am, as unix timestamp
    # as integer with milliseconds precision. The timestamp format is required
    # by the discovergy API, cf. https://api.discovergy.com/docs/
    # start = round(datetime.combine(datetime.now(),
    # datetime.min.time()).timestamp() * 1e3)

    start = datetime.combine(
        datetime.utcnow(), datetime.min.time()).timestamp()
    begin = request.args.get('begin', default=start, type=int)
    return begin


@IndividualConsumptionHistory.route('/individual-consumption-history',
                                    methods=['GET'])
@login_required
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

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST
    begin = read_begin_parameter()
    result = {}

    try:
        readings = get_readings(user.meter_id, begin)
        for key in readings:
            result[key] = readings[key].get('power')

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except ValueError as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT


@GroupConsumptionHistory.route('/group-consumption-history', methods=['GET'])
@login_required
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

    user, group = get_parameters()
    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST
    if group is None:
        return UNKNOWN_GROUP.to_json(), status.HTTP_400_BAD_REQUEST
    begin = read_begin_parameter()
    result = {}
    produced = {}
    consumed = {}

    try:
        readings = get_readings(group.group_meter_id, begin)
        for key in readings:
            produced[key] = readings[key].get('energyOut')
            consumed[key] = readings[key].get('power')

        # Return result
        result["consumed"] = consumed
        result["produced"] = produced
        return jsonify(result), status.HTTP_200_OK

    except TypeError as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
