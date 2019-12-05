
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from models.user import User, ActiveType
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
    user_requested = j['user']
    password_requested = j['password']

    targetUser = User.query.filter_by(name=user_requested).first()
    if targetUser is None:
        return Error('Unknown credentials',
                     'Try again with proper username/password.').to_json(), 401

    if not targetUser.check_password(password_requested):
        return Error('Unknown credentials',
                     'Try again with proper username/password.').to_json(), 401

    if not targetUser.active == ActiveType.ACTIVE:
        return Error('User not active', 'Can not login.').to_json(), 403

    access_token = create_access_token(identity=targetUser.name)
    return jsonify(sessionToken=access_token), 200
