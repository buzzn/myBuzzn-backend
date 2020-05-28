from flask import render_template, Blueprint, Response, request
from flask import current_app as app
from flask_api import status

from models.user import User, StateType, PASSWORD_MAX_LENGTH
from util.database import db
from util.error import Error
from util.translation import get_opening_greeting
from util.mailer import send_mail

ResetPassword = Blueprint('ResetPassword', __name__)


class Errors:
    UNKNOWN_USER = Error('Unknown user', 'No user found')
    DEACTIVATED_USER = Error('User account deactivated',
                             'Can not request new password for deactivated account.')


@ResetPassword.route('/password/request-reset-token', methods=['POST'])
def request_password_reset_token():
    """Requests a new password token. Sends a mail to the user's mail address.
    :param str user: The user's mail address.
    """
    j = request.get_json(force=True)
    user_requested = j['user'].lower()

    # Disabled user accounts can not request for a new password.
    target_user = User.query.filter_by(mail=user_requested).first()

    if target_user is None:
        return Errors.UNKNOWN_USER.make_json_response(status.HTTP_400_BAD_REQUEST)

    if target_user.state == StateType.DEACTIVATED:
        return Errors.DEACTIVATED_USER.make_json_response(status.HTTP_400_BAD_REQUEST)

    target_user.generate_password_request_token()

    send_mail(target_user.mail, render_template("password/reset_password_mail.txt",
                                                greeting=get_opening_greeting(target_user),
                                                wlink="{}/password/reset/{}".format(
                                                    app.config['BUZZN_BASE_URL'],
                                                    target_user.password_reset_token
                                                )), 'Passwort zurücksetzen für Buzzn-App')

    db.session.commit()
    return '', status.HTTP_201_CREATED


@ResetPassword.route('/password/reset/<token>', methods=['GET'])
def reset_password(token):
    return Response(render_template('password/request.html',
                                    passwordResetToken=token))


@ResetPassword.route('/password/reset/<token>', methods=['POST'])
def do_password(token):
    """Resets the password of the user account according to the given token.

    :param str token: The account with this token will set the password.
    :param str password: The new password in plaintext.
    :param str passwordRepeat: The repeated password in plaintext.
    """
    password_reset_token = token
    requested_password = request.form['password']
    requested_password_repeat = request.form['passwordRepeat']

    # Only pending states can be used.
    target_user = User.query.filter_by(
        password_reset_token=password_reset_token).first()

    if target_user is None:
        return Response(render_template('password/failure.html',
                                        message=('Unbekannter token.  Stellen '
                                                 'sie sicher, dass Sie nicht mehrfach '
                                                 'eine Passwortzurücksetzung '
                                                 'angefordert haben und nehmen sie '
                                                 'immer die aktuelle.')))

    if not target_user.state == StateType.PASSWORT_RESET_PENDING:
        return Response(render_template('password/failure.html',
                                        message='User has no pending password reset.'))

    if not requested_password == requested_password_repeat:
        return Response(render_template('password/request.html',
                                        passwordResetToken=token,
                                        message='Passwörter stimmen nicht überein.'))

    if not target_user.check_password_length(requested_password):
        return Response(render_template('password/request.html',
                                        passwordResetToken=token,
                                        message=('Passwort zu kurz. Das '
                                                 'Passwort muss mindestens {} '
                                                 'Zeichen haben').format(PASSWORD_MAX_LENGTH)))

    target_user.set_password(requested_password)
    target_user.state = StateType.ACTIVE
    db.session.commit()

    return Response(render_template('password/success.html'))
