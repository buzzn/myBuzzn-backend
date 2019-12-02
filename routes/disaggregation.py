import os
from datetime import datetime, timedelta
import logging
from flask import Blueprint, jsonify, request
from flask_api import status
from flask import current_app as app
from discovergy.discovergy import Discovergy


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
def individual_disaggregation():
    """ Shows the power curve disaggregation of the given time interval.
    :param int begin: start time of disaggregation, default is 48h back in time
    :param in end: end time of disaggregation, default is $now
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    # pylint: disable=fixme
    # TODO - Set meter id in database
    # TODO - Get meter id from database

    # Call discovergy API for the given meter
    begin, end = read_parameters()
    d = login()
    result = {}
    try:
        readings = d.get_disaggregation(os.environ['METER_ID'], begin, end)
        for reading in readings.items():
            result[reading[0]] = reading[1]

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except TypeError as e:
        logger.error("%s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT


@GroupDisaggregation.route('/group-disaggregation', methods=['GET'])
def group_disaggregation():
    """ Shows the power curve disaggregation of the given time interval.
    :param int begin: start time of disaggregation, default is 48h back in time
    :param int end: end time of disaggregation, default is $now
    :return: ({str => {str => int}}, 200) or ({}, 206) if there is no history
    :rtype: tuple
    """

    # pylint: disable=fixme
    # TODO - Set group meter id in database
    # TODO - Get group meter id from database

    # Call discovergy API for the given group meter
    begin, end = read_parameters()
    d = login()
    result = {}
    try:
        readings = d.get_disaggregation(
            os.environ['GROUP_METER_ID'], begin, end)
        for reading in readings.items():
            result[reading[0]] = reading[1]

        # Return result
        return jsonify(result), status.HTTP_200_OK

    except TypeError as e:
        logger.error("%s", e)

        # Return result
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
