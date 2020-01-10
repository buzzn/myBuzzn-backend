import json
import os
from datetime import datetime, timedelta
import logging
import redis
from flask import Blueprint, jsonify, request
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.user import User
from util.database import db
from util.error import UNKNOWN_USER, UNKNOWN_GROUP
from util.login import login_required, get_parameters


logger = logging.getLogger(__name__)
IndividualDisaggregation = Blueprint('IndividualDisaggregation', __name__)
GroupDisaggregation = Blueprint('GroupDisaggregation', __name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_sorted_keys(meter_id):
    """ Return all keys stored in the redis db for a given meter id.
    :param str meter_id: the meter id to prefix the scan with
    """

    return sorted([key.decode('utf-8') for key in redis_client.scan_iter(meter_id + '*')])


def get_disaggregation(meter_id):
    """ Return all disaggregation values for the given meter id.
    :param str meter_id: the meter id for which to get the values
    """
    result = {}
    for key in get_sorted_keys(meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'disaggregation':
            timestamp = key[len(meter_id):]
            result[timestamp] = data.get('values')
    return result


def read_parameters():
    """ Use the given parameters. """

    # Calculate the minimal time of "today", i.e. 00:00 am, as unix timestamp
    # as integer with milliseconds precision. The timestamp format is required
    # by the discovergy API, cf. https://api.discovergy.com/docs/
    start = round((datetime.now() - timedelta(hours=48)).timestamp() * 1e3)
    begin = request.args.get('begin', default=start, type=int)
    end = request.args.get('end', default=None, type=int)
    return begin, end


@IndividualDisaggregation.route('/individual-disaggregation', methods=['GET'])
@login_required
def individual_disaggregation():
    """ Shows the power curve disaggregation of the given time interval.
    :param int begin: start time of disaggregation, default is 48h back in time
    :param int end: end time of disaggregation, default is $now
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER

    # Get all disaggregation values for the given meter
    result = {}
    try:
        result = get_disaggregation(user.meter_id)

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except (TypeError, AttributeError) as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT


@GroupDisaggregation.route('/group-disaggregation', methods=['GET'])
@login_required
def group_disaggregation():
    """ Shows the power curve disaggregation of the given time interval.
    :param int begin: start time of disaggregation, default is 48h back in time
    :param int end: end time of disaggregation, default is $now
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    user, group = get_parameters()
    if user is None:
        return UNKNOWN_USER
    if group is None:
        return UNKNOWN_GROUP

    # Call discovergy API for the given group meter
    result = {}
    try:
        result = get_disaggregation(group.group_meter_id)

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except (TypeError, AttributeError) as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
