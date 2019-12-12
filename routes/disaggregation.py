import os
from datetime import datetime, timedelta
import logging
from flask import Blueprint, jsonify, request
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from flask import current_app as app
from discovergy.discovergy import Discovergy
from models.user import User
from util.database import db
from util.error import UNKNOWN_USER, UNKNOWN_GROUP
from util.login import login_required, get_parameters


logger = logging.getLogger(__name__)
IndividualDisaggregation = Blueprint('IndividualDisaggregation', __name__)
GroupDisaggregation = Blueprint('GroupDisaggregation', __name__)


def read_parameters():
    """ Use the given parameters. """

    # Calculate the minimal time of "today", i.e. 00:00 am, as unix timestamp
    # as integer with milliseconds precision. The timestamp format is required
    # by the discovergy API, cf. https://api.discovergy.com/docs/
    start = round((datetime.now() - timedelta(hours=48)).timestamp() * 1e3)
    begin = request.args.get('begin', default=start, type=int)
    end = request.args.get('end', default=None, type=int)
    return begin, end


def login():
    """ Authenticate against the discovergy backend. """

    client_name = app.config['CLIENT_NAME']
    d = Discovergy(client_name)
    d.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    return d


@IndividualDisaggregation.route('/individual-disaggregation', methods=['GET'])
@login_required
def individual_disaggregation():
    """ Shows the power curve disaggregation of the given time interval.
    :param int begin: start time of disaggregation, default is 48h back in time
    :param in end: end time of disaggregation, default is $now
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER

    # Call discovergy API for the given meter
    begin, end = read_parameters()
    d = login()
    result = {}
    try:
        readings = d.get_disaggregation(user.meter_id, begin, end)
        for reading in readings.items():
            result[reading[0]] = reading[1]

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
    begin, end = read_parameters()
    d = login()
    result = {}
    try:
        readings = d.get_disaggregation(group._group_meter_id, begin, end)
        for reading in readings.items():
            result[reading[0]] = reading[1]

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except (TypeError, AttributeError) as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
