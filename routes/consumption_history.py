import json
import os
from datetime import datetime, timedelta
import logging.config
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
from util.redis_helpers import get_sorted_keys, get_sorted_keys_date_prefix, get_entry_date
from util.websocket_provider import get_group_members


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

        reading_date, data = get_entry_date(redis_client, meter_id, key, 'reading')

        if reading_date is None or data is None:
            continue

        # Parse timestamp as int to use consistent timestamps
        reading_timestamp = int(reading_date.timestamp())

        if reading_timestamp >= begin:
            result[reading_date.strftime('%Y-%m-%d %H:%M:%S')] = data.get('values')

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

        reading_date, data = get_entry_date(redis_client, meter_id, key, 'reading')

        if reading_date is None or data is None:
            continue

        result[reading_date.strftime('%Y-%m-%d %H:%M:%S')] = data.get('values')

    return result


def get_first_and_last_energy_for_date(meter_id, date):
    """ Returns first and last energy consumption for a given meter_id of today
    :param str meter_id: the meter id for which to get the values
    :param str date: the date for which to get the values
    :return: the first and last energy consumption of date mapped to their timestamps
    :rtype: dict
    """
    result = {}

    try:
        key_first = f"{meter_id}_{date}_first"
        data = json.loads(redis_client.get(key_first))

        if data is not None:
            result[data.get("time")] = data.get('values').get('energy')

    except Exception as e:
        message = 'No first reading available for date {}: {}'.format(
            date, e)
        logger.error(message)

    try:
        key_last = f"{meter_id}_{date}_last"
        data = json.loads(redis_client.get(key_last))

        if data is not None:
            result[data.get("time")] = data.get('values').get('energy')

    except Exception as e:
        message = 'No last reading available for date {}: {}'.format(
                        date, e)
        logger.error(message)

    return result


def get_average_power_for_meter_id_and_date(meter_id, date):
    """ Return date's average power values for the given meter id per 15 minutes.
    :param str meter_id: the meter id for which to get the values
    :param datetime date: the date for which to get the values
    :return: the average power values mapped to their timestamps
    :rtype: dict
    """
    average_power = {}

    try:
        key_average_power = f"average_power_{meter_id}_{date}"
        data = json.loads(redis_client.get(key_average_power))
        average_power = data

    except Exception as e:
        message = f"No average power available for {meter_id} " \
                  f"for date {date}: {e}"
        logger.error(message)

    return average_power


def create_member_data(member):
    """ Create a data package for a group member.
    :param dict member: a group member's parameters
    :return: a group member data package
    :rtype: dict
    """

    today = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')
    member_meter_id = member.get('meter_id')

    # Get today's average power values per 15 minutes
    member_powers = get_average_power_for_meter_id_and_date(member_meter_id, today)

    # Get first and last energy consumption of today
    member_consumptions = get_first_and_last_energy_for_date(member_meter_id, today)

    return dict(power=member_powers, energy=member_consumptions)


@IndividualConsumptionHistory.route('/individual-consumption-history',
                                    methods=['GET'])
@login_required
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval in mW and
    the meter readings in μWh.
    :param int begin: start value as unixtime, default is today at 00:00:00
    :return: (a JSON object with each power consumption/meter reading mapped to its timestamp, 200)
    or ({}, 206) if there is no history
    :rtype: tuple
    swagger_from_file: swagger_files/get_individual-consumption-history.yml
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()

    if user is None:
        return UNKNOWN_USER.make_json_response(status.HTTP_400_BAD_REQUEST)
    begin = read_begin_parameter()

    result = {}

    try:
        if begin is None:
            begin = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')
        else:
            begin = datetime.strftime(datetime.fromtimestamp(begin), '%Y-%m-%d')

        energy = get_first_and_last_energy_for_date(user.meter_id, begin)
        power = get_average_power_for_meter_id_and_date(user.meter_id, begin)

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
    """ Shows the history of consumption of today in mW.
    :return: (a JSON object with each meter reading/power consumption/power
    production mapped to its timestamp, 200)
    or ({}, 206) if there is no history
    :rtype: tuple
    swagger_from_file: swagger_files/get_group-consumption-history.yml
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER.make_json_response(status.HTTP_400_BAD_REQUEST)
    group = db.session.query(Group).filter_by(id=user.group_id).first()
    if group is None:
        return UNKNOWN_GROUP.make_json_response(status.HTTP_400_BAD_REQUEST)

    group_users = {}

    try:
        today = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')

        # Group community consumption meter
        # Get today's average consumed power per 15 minutes
        consumed_power = get_average_power_for_meter_id_and_date(group.group_meter_id, today)
        # Get first and last group energy consumption of today
        consumed_energy = get_first_and_last_energy_for_date(group.group_meter_id, today)

        # First group production meter
        # Get today's average production power for first production meter per 15 minutes
        produced_first_meter_power = get_average_power_for_meter_id_and_date(
            group.group_production_meter_id_first, today)
        # Get first and last group energy production of first production meter of today
        produced_first_meter_energy = get_first_and_last_energy_for_date(
            group.group_production_meter_id_first, today)

        # Second group production meter
        # Get today's average production power for second production meter per 15 minutes
        produced_second_meter_power = get_average_power_for_meter_id_and_date(
            group.group_production_meter_id_second, today)
        # Get first and last group energy production of first production meter of today
        produced_second_meter_energy = get_first_and_last_energy_for_date(
            group.group_production_meter_id_second, today)

        # Group members
        for member in get_group_members(user_id):
            member_data = create_member_data(member)
            group_users[member.get('id')] = member_data

        # Return result
        return jsonify(dict(consumed_power=consumed_power,
                            produced_first_meter_power=produced_first_meter_power,
                            produced_second_meter_power=produced_second_meter_power,
                            consumed_energy=consumed_energy,
                            produced_first_meter_energy=produced_first_meter_energy,
                            produced_second_meter_energy=produced_second_meter_energy,
                            group_users=group_users)), status.HTTP_200_OK

    except TypeError as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify({}), status.HTTP_206_PARTIAL_CONTENT
