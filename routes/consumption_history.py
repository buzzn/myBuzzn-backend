import json
import os
from datetime import datetime, timedelta
import logging.config
from dateutil import parser
import redis
from flask import Blueprint, jsonify
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.group import Group
from models.user import User
from routes.disaggregation import read_begin_parameter
from util.database import db
from util.error import UNKNOWN_USER, UNKNOWN_GROUP
from util.login import login_required
from util.redis_helpers import get_sorted_keys, get_sorted_keys_date_prefix


logger = logging.getLogger(__name__)
IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)
GroupConsumptionHistory = Blueprint('GroupConsumptionHistory', __name__)
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
    :return: the readings for the period mapped to their timestamps
    :rtype: dict
    """

    result = {}
    for key in get_sorted_keys(redis_client, meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'reading':
            reading_date = parser.parse(key[len(meter_id)+1:])

            # Parse timestamp as int to use consistent timestamps
            reading_timestamp = int(reading_date.timestamp())

            if reading_timestamp >= begin:
                result[reading_date.strftime(
                    '%Y-%m-%d %H:%M:%S')] = data.get('values')

    return result


def get_default_readings(meter_id):
    """ Return all readings for the given meter id, starting yesterday.
    :param str meter_id: the meter id for which to get the values
    :return: the readings for the period mapped to their timestamps
    :rtype: dict
    """

    result = {}

    # Get yesterday's date
    yesterday = datetime.strftime(datetime.utcnow() - timedelta(hours=24),
                                  '%Y-%m-%d')

    # Get today's date
    today = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')

    # Get data from yesterday until now
    redis_keys = get_sorted_keys_date_prefix(redis_client, meter_id, yesterday) +\
        get_sorted_keys_date_prefix(redis_client, meter_id, today)

    for key in redis_keys:
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'reading':
            reading_date = parser.parse(key[len(meter_id)+1:])
            result[reading_date.strftime(
                '%Y-%m-%d %H:%M:%S')] = data.get('values')

    return result


@IndividualConsumptionHistory.route('/individual-consumption-history',
                                    methods=['GET'])
@login_required
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval in mW and
    the meter readings in μWh.
    :param int begin: start value as unixtime, default is yesterday at 00:00:00
    :return: (a JSON object with each power consumption/meter reading mapped to its timestamp, 200)
    or ({}, 206) if there is no history
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
        if begin is None:
            readings = get_default_readings(user.meter_id)
        else:
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
    :param int begin: start value as unixtime, default is yesterday at 00:00:00
    :param str tics: time distance between returned readings with possible
    values 'raw', 'three_minutes', 'fifteen_minutes', 'one_hour', 'one_day',
    'one_week', 'one_month', 'one_year' (default is 'one_hour')
    :return: (a JSON object with each meter reading/power consumption/power
    production mapped to its timestamp, 200)
    or ({}, 206) if there is no history
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
        if begin is None:
            readings = get_default_readings(group.group_meter_id)
        else:
            readings = get_readings(group.group_meter_id, begin)
        for key in readings:
            consumed_power[key] = readings[key].get('power')
            consumed_energy[key] = readings[key].get('energy')

        # First group production meter
        if begin is None:
            readings = get_default_readings(
                group.group_production_meter_id_first)
        else:
            readings = get_readings(
                group.group_production_meter_id_first, begin)
        for key in readings:
            produced_first_meter_power[key] = readings[key].get('power')
            produced_first_meter_energy[key] = readings[key].get('energy')

        # Second group production meter
        if begin is None:
            readings = get_default_readings(
                group.group_production_meter_id_second)
        else:
            readings = get_readings(group.group_production_meter_id_second,
                                    begin)
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
