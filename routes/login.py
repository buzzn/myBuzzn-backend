from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from flask_api import status
from flask_jwt_extended import create_access_token
from flask import current_app as app

from util.database import db

from models.user import User, StateType, BaselineStateType
from util.error import Error

Login = Blueprint('Login', __name__)


def set_baseline_state(user_id):
    """ Sets the baseline state of a given user depending on the baseline and
        the registration date of the user.
        :param str user_id: the user's id
        """
    target_user = db.session.query(User).filter_by(id=user_id).first()
    if not target_user.baseline_state == BaselineStateType.READY:
        if target_user.baseline is not None:
            target_user.baseline_state = BaselineStateType.READY
        else:
            if target_user.registration_date is None:
                target_user.baseline_state = BaselineStateType.WAITING_FOR_DATA
            else:
                time_diff = datetime.utcnow() - target_user.registration_date
                if time_diff <= timedelta(hours=24):
                    target_user.baseline_state = BaselineStateType.WAITING_FOR_DATA
                else:
                    target_user.baseline_state = BaselineStateType.NO_READINGS_AVAILABLE
    db.session.add(target_user)
    db.session.commit()


@Login.route('/login', methods=['POST'])
def login():
    """Performs a login for the given user credentials.
    :param str user: The user's name to login.
    :param str password: The user's password in plaintext to login.
    :returns:
      200: If the login was successful.
      401: If either user name was not found or password does not match.
      404: If the useraccount is not active.
    swagger_from_file: swagger_files/post_login.yml
    """
    j = request.get_json(force=True)
    user_requested = j['user'].lower()
    password_requested = j['password']

    target_user = User.query.filter_by(mail=user_requested).first()

    if target_user is None:
        return (Error('Unknown credentials',
                      'Try again with proper username/password.').to_json(),
                status.HTTP_401_UNAUTHORIZED)

    if not target_user.check_password(password_requested):
        return (Error('Unknown credentials',
                      'Try again with proper username/password.').to_json(),
                status.HTTP_401_UNAUTHORIZED)

    if not target_user.state == StateType.ACTIVE:
        return Error('User not active', 'Can not login.').to_json(), status.HTTP_403_FORBIDDEN

    set_baseline_state(target_user.id)

    access_token = create_access_token(identity=target_user.id)
    expired_timestamp = (datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']).timestamp()

    return jsonify(sessionToken=access_token,
                   expiredTimestamp=expired_timestamp), status.HTTP_200_OK
