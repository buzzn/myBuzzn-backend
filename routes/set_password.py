from flask import Blueprint, request
from flask_api import status

from models.user import User, ActiveType
from util.error import Error
from util.database import db

SetPassword = Blueprint('SetPassword', __name__)


class Errors:
    UNKNOWN_USER = Error('Unknown user', 'No user found')
    WRONG_TOKEN = Error('Wrong token', 'Check token and try again.')
    NO_ACTIVATION_PENDING = Error('No Activation pending',
                                  'There is no activation pending for this user.')
    PASSWORD_TOO_SHORT = Error('Password too short',
                               'Provide a longer password and try again')


@SetPassword.route('/set-password', methods=['POST'])
def setPassword():
    """Set the password for an user who's activation is still pending.
    :param str user: The target user's name.
    :param str token: The target user's token.
    :param str password: The target user's password in plaintext to set.
    :returns:
        200: If the account has been activated successfully.
        400: If activation_token does not match or user account is not in state pending.
        404: If the user is not found.
    """
    j = request.get_json(force=True)
    user_requested = j['user']
    token = j['token']
    password_requested = j['password']

    targetUser = User.query.filter_by(_name=user_requested).first()

    if targetUser is None:
        return Errors.UNKNOWN_USER.to_json(), status.HTTP_404_NOT_FOUND

    if targetUser.get_activation_token() != token:
        return Errors.WRONG_TOKEN.to_json(), status.HTTP_400_BAD_REQUEST

    if targetUser.get_status() != ActiveType.ACTIVATION_PENDING:
        return Errors.NO_ACTIVATION_PENDING.to_json(), status.HTTP_400_BAD_REQUEST

    if len(password_requested) < 8:
        return Errors.PASSWORD_TOO_SHORT.to_json(), status.HTTP_400_BAD_REQUEST

    targetUser.set_password(password_requested)
    targetUser.activate()

    db.session.commit()
    return '', status.HTTP_200_OK
