import json
import os
from datetime import datetime
import logging.config
from dateutil import parser
import redis
from flask import Blueprint, jsonify, request
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.group import Group
from models.user import User
from util.database import db
from util.error import UNKNOWN_USER, UNKNOWN_GROUP
from util.login import login_required
from util.redis_helpers import get_sorted_keys


logger = logging.getLogger(__name__)
IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)
GroupConsumptionHistory = Blueprint('GroupConsumptionHistory', __name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_all_readings(meter_id):
    """ Return all readings for the given meter id.
    :param str meter_id: the meter id for which to get the values
    """

    result = {}
    for key in get_sorted_keys(redis_client, meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'reading':
            timestamp = key[len(meter_id)+1:]
            result[timestamp] = data.get('values')
    return result


def get_readings(meter_id, begin):
    """ Return all readings for the given meter id, starting with the given
    timestamp. As we were using unix timestamps as basis for our dates all
    along, there is no need to convert the given, timezone-unaware dates to UTC.
    :param str meter_id: the meter id for which to get the values
    :param int begin: the unix timestamp to begin with
    """

    result = {}
    for key in get_sorted_keys(redis_client, meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'reading':
            reading_date = parser.parse(key[len(meter_id)+1:])
            reading_timestamp = reading_date.timestamp()
            if reading_timestamp >= begin:
                result[reading_date.strftime(
                    '%Y-%m-%d %H:%S:%M')] = data.get('values')
    return result


def read_begin_parameter():
    """ Use the given begin parameter. """

    # Calculate the minimal time of "today", i.e. 00:00 am as unix timestamp

    start = datetime.combine(
        datetime.utcnow(), datetime.min.time()).timestamp()
    begin = request.args.get('begin', default=start, type=float)
    return begin


@IndividualConsumptionHistory.route('/individual-consumption-history',
                                    methods=['GET'])
@login_required
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval in mW and
    the meter readings in μWh.
    :param int begin: start time of consumption, default is today at 0:00
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
    power = {}
    energy = {}

    try:
        readings = get_readings(user.meter_id, begin)
        for key in readings:
            power[key] = readings[key].get('power')
            energy[key] = readings[key].get('energy')

        # Return result
        result['energy'] = energy
        result['power'] = power
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
    :return: (dict with values, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST
    group = db.session.query(Group).filter_by(id=user.group_id).first()
    if group is None:
        return UNKNOWN_GROUP.to_json(), status.HTTP_400_BAD_REQUEST

    begin = read_begin_parameter()
    result = {}
    consumed_power = {}
    produced_first_meter_power = {}
    produced_second_meter_power = {}
    consumed_energy = {}
    produced_first_meter_energy = {}
    produced_second_meter_energy = {}

    try:

        # Group community consumption meter
        readings = get_readings(group.group_meter_id, begin)
        for key in readings:
            consumed_power[key] = readings[key].get('power')
            consumed_energy[key] = readings[key].get('energy')

        # First group production meter
        readings = get_readings(group.group_production_meter_id_first, begin)
        for key in readings:
            produced_first_meter_power[key] = readings[key].get('power')
            produced_first_meter_energy[key] = readings[key].get('energy')

        # Second group production meter
        readings = get_readings(group.group_production_meter_id_second, begin)
        for key in readings:
            produced_second_meter_power[key] = readings[key].get(
                'power')
            produced_second_meter_energy[key] = readings[key].get(
                'energy')

        # Return result
        result['consumed_power'] = consumed_power
        result['produced_first_meter_power'] = produced_first_meter_power
        result['produced_second_meter_power'] = produced_second_meter_power
        result['consumed_energy'] = consumed_energy
        result['produced_first_meter_energy'] = produced_first_meter_energy
        result['produced_second_meter_energy'] = produced_second_meter_energy
        return jsonify(result), status.HTTP_200_OK

    except TypeError as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
