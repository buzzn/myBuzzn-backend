from enum import Enum
import bcrypt
from flask import current_app
from sqlalchemy import ForeignKey
from util.database import db


class RoleType(Enum):
    """Indicates the role of a user account. This may privilege the user for
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
    """Represents a user account in the backend.
    """
    @staticmethod
    def NAME_MAX_LENGTH():
        return 50

    @staticmethod
    def PASSWORD_MAX_LENGTH():
        return 129

    @staticmethod
    def generate_password_hash(target):
        """Generates a password hash for the given password using the app's
        spassword salt.
        :param str target: The plaintext password to generate the hash for
        :return: The hashed password.
        :rtype: str
        """
        return bcrypt.hashpw(target.encode('utf-8'),
                             current_app.config['PASSWORD_SALT'])

    _id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(33), unique=True)
    _activation_token = db.Column(db.String(33), unique=True)
    _password = db.Column(db.String(333))
    _status = db.Column(db.Enum(ActiveType))
    _role = db.Column(db.Enum(RoleType))
    _meter_id = db.Column(db.String(32))
    _inhabitants = db.Column(db.Integer)
    _flat_size = db.Column(db.Float)
    _group_id = db.Column(db.Integer, ForeignKey('group._id'))

    def __init__(self, name, activation_token, meter_id, group_id):
        """Creates a new user account and sets its state to pending.
        :param str name: The user's name.
        :param str activation_token: Token to activate the account.
        :param str meter_id: the user's meter id
        :parem int group: the user's group id
        """
        self._name = name
        self._activation_token = activation_token
        self._status = ActiveType.ACTIVATION_PENDING
        self._role = RoleType.LOCAL_POWER_TAKER
        self._meter_id = meter_id
        self._group_id = group_id

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

    def get_meter_id(self):
        return self._meter_id

    def set_inhabitants(self, inhabitants):
        self._inhabitants = inhabitants

    def get_inhabitants(self):
        return self._inhabitants

    def set_flat_size(self, flat_size):
        self._flat_size = flat_size

    def get_flat_size(self):
        return self._flat_size

    def get_group(self):
        return self._group

    def is_active(self):
        """Returns a value indicating whether this account is active.
        :return: True, if this account is active, False otherwise.
        :rtype: bool
        """
        return self._status == ActiveType.ACTIVE

    def check_password(self, password_to_check):
        """Checks whether the given password matches the user's.
        :param str password_to_check: Password in plaintext.
        :return: True if the passwort matches, False otherwise.
        :rtype: bool
        """
        return bcrypt.checkpw(User.generate_password_hash(password_to_check),
                              self._password)

    def set_password(self, newPassword):
        """Sets the user's password.
        :param self:
        :param newPassword: The new password in plaintext.
        """
        self._password = User.generate_password_hash(newPassword)

    def activate(self):
        """Activates the account if it is pending."""
        if self._status == ActiveType.ACTIVATION_PENDING:
            self._status = ActiveType.ACTIVE
