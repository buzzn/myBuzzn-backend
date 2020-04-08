from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_api import status
from flask_jwt_extended import create_access_token
from flask import current_app as app

from models.user import User, StateType
from util.error import Error

Login = Blueprint('Login', __name__)


@Login.route('/login', methods=['POST'])
def login():
    """Performs a login for the given user credentials.
    :param str user: The user's name to login.
    :param str password: The user's password in plaintext to login.
    :returns:
      200: If the login was successful.
      401: If either user name was not found or password does not match.
      404: If the useraccount is not active.
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

    access_token = create_access_token(identity=target_user.id)
    expired_timestamp = (datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']).timestamp()
    return jsonify(sessionToken=access_token,
                   expiredTimestamp=expired_timestamp), status.HTTP_200_OK
