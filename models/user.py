from enum import Enum
import bcrypt
from flask import current_app
from util.database import db


class RoleType(Enum):
    """Indicates the role of a user account. This may privilige the user for
    specific actions.
    """
    LOCAL_POWER_TAKER = 'Local powertaker in a local pool'
    ADMINISTRATOR = 'Administrator'


class ActiveType(Enum):
    """Indicates the user account's state in its lifecycle.
    """
    ACTIVATION_PENDING = 'User activation pending.'
    ACTIVE = 'User account is active.'
    DISABLED = 'User account is disabled'


class User(db.Model):
    """Represents an user account in the backend.

    Arguments:
        db {class} -- Db related stuff to crud an instance of this class.
    """
    @staticmethod
    def NAME_MAX_LENGTH():
        return 50

    @staticmethod
    def PASSWORD_MAX_LENGTH():
        return 129

    @staticmethod
    def generate_password_hash(target):
        """Generates a password hash for the given password using app's
        spassword salt.

        Arguments:
            target {String} -- The plaintext password to generate the hash for

        Returns:
            String -- The hash.
        """
        return bcrypt.hashpw(target.encode('utf-8'),
                             current_app.config['PASSWORD_SALT'])

    _id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(33), unique=True)
    _activation_token = db.Column(db.String(33), unique=True)
    _password = db.Column(db.String(333))
    _status = db.Column(db.Enum(ActiveType))
    _role = db.Column(db.Enum(RoleType))

    def __init__(self, name, activation_token):
        """Creates a new useraccount and sets its state into pending.

        Arguments:
            name {String} -- The user's name.
            activation_token {String} -- Token to activate the account.
        """
        self._name = name
        self._activation_token = activation_token
        self._status = ActiveType.ACTIVATION_PENDING
        self._role = RoleType.LOCAL_POWER_TAKER

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_activation_token(self):
        return self._activation_token

    def get_status(self):
        return self._status

    def get_role(self):
        return self._role

    def is_active(self):
        """Returns a value indicating whether this account is active.

        Returns:
            Boolean -- True, if this account is active, false otherwise.
        """
        return self._status == ActiveType.ACTIVE

    def check_password(self, password_to_check):
        """Checks whether the given password matches the user's.

        Arguments:
            password_to_check {String} -- Password in plaintext.

        Returns:
            Boolean -- True if the passwort matches, false otherwise.
        """
        return bcrypt.checkpw(User.generate_password_hash(password_to_check),
                              self._password)

    def set_password(self, newPassword):
        """Sets the user's password.

        Arguments:
            newPassword {String} -- The new password in plaintext.
        """
        self._password = User.generate_password_hash(newPassword)

    def activate(self):
        """Activates the account if it is pending."""
        if self._status == ActiveType.ACTIVATION_PENDING:
            self._status = ActiveType.ACTIVE
