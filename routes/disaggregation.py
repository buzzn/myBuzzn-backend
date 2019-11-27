import os
from datetime import datetime
import logging
from flask import Blueprint, jsonify, request
from discovergy.discovergy import Discovergy
from flask import current_app as app


logger = logging.getLogger(__name__)
IndividualDisaggregation = Blueprint('IndividualDisaggregation', __name__)
GroupDisaggregation = Blueprint('GroupDisaggregation', __name__)


def read_parameters():
    """ Use the given parameters. """
    start = round(datetime.combine(datetime.now(),
                                   datetime.min.time()).timestamp() * 1e3)
    begin = request.args.get('begin', default=start, type=int)
    end = request.args.get('end', default=None, type=int)
    return begin, end


@IndividualDisaggregation.route('/individual-disaggregation', methods=['GET'])
def individual_disaggregation():
    """ TODO
    """

    # TODO - Set meter id in database
    # TODO - Get meter id from database

    # Call discovergy API for the given meter
    begin, end = read_parameters()
    client_name = app.config['CLIENT_NAME']
    d = Discovergy(client_name)
    d.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    result = {}
    try:
        readings = d.get_disaggregation(os.environ['METER_ID'], begin, end)
        for reading in readings:
            result[reading.get('time')] = reading.get('values')

        # Return result
        return jsonify(result), 200

    except TypeError as e:
        logger.error("Exception: %s", e)

        # Return result
        return jsonify(result), 206
