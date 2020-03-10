import logging.config
from flask import Blueprint, jsonify
from flask_api import status
from flask_jwt_extended import get_jwt_identity
from models.user import User
from models.savings import UserSaving, CommunitySaving
from models.baseline import BaseLine
from util.database import db, get_engine, create_session
from util.error import UNKNOWN_USER, NO_GLOBAL_CHALLENGE, NO_BASELINE, exception_message
from util.login import login_required


logger = logging.getLogger(__name__)
IndividualGlobalChallenge = Blueprint('IndividualGlobalChallenge',
                                      __name__)
CommunityGlobalChallenge = Blueprint('CommunityGlobalChallenge', __name__)


def get_individual_saving(meter_id):
    """ Retrieve the last individual saving prognosis for the given meter id
    from the SQLite database.
    :param str meter_id: the user's meter id
    :returns: the last saving together with its timestamp or None if there are
    no values
    :rtype: dict or type(None) if there are no values
    """

    # pylint: disable=line-too-long
    #query = "SELECT timestamp, saving FROM user_saving WHERE meter_id = '%s' ORDER BY timestamp DESC" % meter_id


    try:
        engine = get_engine()
        with engine.connect():

            # Query last individual saving prognosis for the given meter id
            query_result = []
            session = create_session()
            for row in session.query(UserSaving) \
                    .filter(UserSaving.meter_id == meter_id).order_by(UserSaving.timestamp.desc()):
                query_result.append((row.timestamp, row.saving))

            individual_saving = query_result.first()

            timestamp = individual_saving[0].split('.')[0]
            saving = individual_saving[1]
            return {timestamp: saving}

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None


def get_individual_baseline(meter_id):
    """ Retrieve the last baseline value for the given meter id from the SQLite
    database.
    :param str meter_id: the user's meter id
    :returns: the last baseline value together with its timestamp or None if
    there are no values
    :rtype: dict or type(None) if there are no values
    """

    # pylint: disable=line-too-long
    # query = "SELECT timestamp, baseline FROM base_line WHERE meter_id = '%s' ORDER BY timestamp DESC" % meter_id

    try:
        engine = get_engine()
        with engine.connect():

            # Query last baseline value for the given meter id
            query_result = []
            session = create_session()
            for row in session.query(BaseLine) \
                    .filter(BaseLine.meter_id == meter_id).order_by(BaseLine.timestamp.desc()):
                query_result.append((row.timestamp, row.baseline))

            individual_baseline = query_result.first()

            timestamp = individual_baseline[0].split('.')[0]
            baseline = individual_baseline[1]
            return {timestamp: baseline}

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None


def get_community_saving():
    """ Retrieve the last community saving prognosis from the SQLite database.
    :returns: the last saving together with its timestamp or None if there are
    no values
    :rtype: dict or type(None) if there are no values
    """

    # query = "SELECT timestamp, saving FROM community_saving ORDER BY timestamp DESC"

    try:
        engine = get_engine()
        with engine.connect():

            # Query last community saving prognosis
            query_result = []
            session = create_session()
            for row in session.query(CommunitySaving).order_by(CommunitySaving.timestamp.desc()):
                query_result.append((row.timestamp, row.saving))

            community_saving = query_result.first()

            timestamp = community_saving[0].split('.')[0]
            saving = community_saving[1]
            return {timestamp: saving}

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return None


@IndividualGlobalChallenge.route('/individual-global-challenge', methods=['GET'])
@login_required
def individual_global_challenge():
    """ Shows the individual saving prognosis for today in μWh.
    :return: (a JSON object where the saving is mapped to the timestamp, 200) or
    ({}, 206) if there is no value
    :rtype: tuple
    """

    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user is None:
        return UNKNOWN_USER.to_json(), status.HTTP_400_BAD_REQUEST

    result = {}

    try:
        saving = get_individual_saving(user.meter_id)
        if saving is None:
            return NO_GLOBAL_CHALLENGE.to_json(), status.HTTP_206_PARTIAL_CONTENT

        baseline = get_individual_baseline(user.meter_id)
        if baseline is None:
            return NO_BASELINE.to_json(), status.HTTP_206_PARTIAL_CONTENT

        result['saving'] = saving
        result['baseline'] = baseline

        return jsonify(result), status.HTTP_200_OK

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT


@CommunityGlobalChallenge.route('/community-global-challenge', methods=['GET'])
def community_global_challenge():
    """ Shows the community saving prognosis for today in μWh.
    :return: (a JSON object where the saving is mapped to the timestamp, 200)
    or ({}, 206) if there is no value
    :rtype: tuple
    """

    result = {}

    try:
        result = get_community_saving()
        return jsonify(result), status.HTTP_200_OK

    except Exception as e:
        message = exception_message(e)
        logger.error(message)
        return jsonify(result), status.HTTP_206_PARTIAL_CONTENT
