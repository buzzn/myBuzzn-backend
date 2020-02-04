import json
import os
from datetime import datetime, timedelta
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
from util.redis_helpers import get_sorted_keys


logger = logging.getLogger(__name__)
IndividualDisaggregation = Blueprint('IndividualDisaggregation', __name__)
GroupDisaggregation = Blueprint('GroupDisaggregation', __name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)


def get_disaggregation(meter_id, begin):
    """ Return all disaggregation values for the given meter id, starting with
    the given timestamp. As we were using unix timestamps as basis for our
    dates all along, there is no need to convert the given,
    timezone-unaware dates to UTC.
    :param str meter_id: the meter id for which to get the values
    :param int begin: the unix timestamp to begin with
    """

    result = {}
    for key in get_sorted_keys(redis_client, meter_id):
        data = json.loads(redis_client.get(key))
        if data.get('type') == 'disaggregation':
            disaggregation_date = parser.parse(key[len(meter_id)+1:])
            disaggregation_timestamp = disaggregation_date.timestamp()
            if disaggregation_timestamp >= begin:
                result[disaggregation_date.strftime(
                    '%Y-%m-%d %H:%M:%S')] = data.get('values')
    return result


def read_begin_parameter():
    """ Use the given begin parameter. """

    # Calculate the minimal time of "today", i.e. 00:00 am as unix timestamp

    start = (datetime.utcnow() - timedelta(hours=48)).timestamp()
    begin = request.args.get('begin', default=start, type=int)
    return begin


@IndividualDisaggregation.route('/individual-disaggregation', methods=['GET'])
@login_required
def individual_disaggregation():
    """ Shows the power curve disaggregation of the given time interval.
    :param int begin: start time of disaggregation, default is 48h back in time
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST

    begin = read_begin_parameter()
    result = {}

    try:
        result = get_disaggregation(user.meter_id, begin)

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
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    user, group = get_parameters()
    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST
    if group is None:
        return UNKNOWN_GROUP.to_json(), status.HTTP_BAD_REQUEST
    begin = read_begin_parameter()
    result = {}

    try:
        result = get_disaggregation(group.group_meter_id, begin)

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except (TypeError, AttributeError) as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
