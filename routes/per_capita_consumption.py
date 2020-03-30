import logging.config
from flask import Blueprint, jsonify
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.pkv import PKV
from models.user import User
from util.database import db
from util.error import UNKNOWN_USER, NO_PER_CAPITA_CONSUMPTION, exception_message
from util.login import login_required


logger = logging.getLogger(__name__)
PerCapitaConsumption = Blueprint('PerCapitaConsumption', __name__)


def get_moving_average_annualized(meter_id):
    """ Retrieve the last annualized moving average for the given meter id from the SQLite database.
    :param str meter_id: the user's meter id
    :returns: the last per capita consumption mapped to its timestamp or None if there are no
    values
    :rtype: dict or type(None) if there are no values
    """

    try:
        result = db.session.query(PKV.date, PKV.moving_average_annualized).filter_by(
            meter_id=meter_id).order_by(PKV.date.desc()).first()

        timestamp = result[0].strftime('%Y-%m-%d %H:%M:%S')
        moving_average_annualized = result[1]
        return {timestamp: moving_average_annualized}

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None


@PerCapitaConsumption.route('/per-capita-consumption', methods=['GET'])
@login_required
def per_capita_consumption():
    """ Shows the the last annualized moving average in kWh.
    :returns: (a JSON object where the moving average is mapped to the
    timestamp, 200) or ({}, 206) if there is no value
    :rtype: tuple
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()

    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST

    result = {}

    try:
        result = get_moving_average_annualized(user.meter_id)
        if result is None:
            return NO_PER_CAPITA_CONSUMPTION.to_json(), status.HTTP_206_PARTIAL_CONTENT

        return jsonify(result), status.HTTP_200_OK

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
