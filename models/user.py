from datetime import datetime, timedelta
from enum import Enum
import secrets

import bcrypt
from flask import current_app as app
from sqlalchemy import ForeignKey
from util.database import db

PASSWORD_MAX_LENGTH = 7


class GenderType(Enum):
    """Indicates the user's gender.
    """
    FEMALE = 'The gender considered for women'
    MALE = 'The gender considered for men'


class RoleType(Enum):
    """Indicates the role of a user account. This may privilege the user for
    specific actions.
    """
    LOCAL_POWER_TAKER = 'Local powertaker in a local pool'
    ADMINISTRATOR = 'Administrator'


class StateType(Enum):
    """Indicates the user account's state in its lifecycle.
    """
    ACTIVATION_PENDING = 'User activation pending.'
    PASSWORT_RESET_PENDING = 'User requested a password change'
    ACTIVE = 'User account is active.'
    DISABLED = 'User account is disabled'

# Maybe setters should not count as public.
#pylint: disable=too-many-public-methods
class User(db.Model):
    """Represents a user account in the backend.
    """
    @staticmethod
    def NAME_MAX_LENGTH():
        return User._name.property.columns[0].type.length

    @staticmethod
    def PASSWORD_MAX_LENGTH():
        return User._password.property.columns[0].type.length

    @staticmethod
    def generate_password_hash(target):
        """Generates a password hash for the given password using the app's
        spassword salt.
        :param str target: The plaintext password to generate the hash for
        :return: The hashed password.
        :rtype: str
        """
        return bcrypt.hashpw(target.encode('utf-8'),
                             bytes.fromhex(app.config['PASSWORD_SALT']))

    @staticmethod
    def check_password_length(new_password):
        """Checks whether the given password matches the password length
            condition.
        :param str new_password: password to check in plaintext
        :returns: True if the given password is too long, False otherwise.
        :rtype: bool
        """
        return len(new_password) > PASSWORD_MAX_LENGTH

    _id = db.Column(db.Integer, primary_key=True)
    _gender = db.Column(db.Enum(GenderType))
    _name = db.Column(db.String(33), unique=True)
    _mail = db.Column(db.String(33))
    _activation_token = db.Column(db.String(33), unique=True)
    _password = db.Column(db.String(333))
    _state = db.Column(db.Enum(StateType))
    _role = db.Column(db.Enum(RoleType))
    _meter_id = db.Column(db.String(32))
    _inhabitants = db.Column(db.Integer)
    _flat_size = db.Column(db.Float)
    _group_id = db.Column(db.Integer, ForeignKey('group._id'))
    _password_reset_token = db.Column(db.String(33), unique=True)
    _password_reset_token_expiries = db.Column(db.DateTime)

    # Plain value constructor, too many arguments is ok here
    #pylint: disable=too-many-arguments
    def __init__(self, gender, name, mail, activation_token, meter_id, group_id):
        """Creates a new user account and sets its state to pending.
        :param gender: The user's gender.
        :param str name: The user's name.
        :param str name: The user's mail address.
        :param str activation_token: Token to activate the account.
        :param str meter_id: the user's meter id
        :param int group_id: the user's group id
        """
        self._gender = gender
        self._name = name
        self._mail = mail
        self._activation_token = activation_token
        self._state = StateType.ACTIVATION_PENDING
        self._role = RoleType.LOCAL_POWER_TAKER
        self._meter_id = meter_id
        self._group_id = group_id

    def get_id(self):
        return self._id

    def get_gender(self):
        return self._gender

    def get_name(self):
        return self._name

    def get_mail(self):
        return self._mail

    def get_activation_token(self):
        return self._activation_token

    def get_state(self):
        return self._state

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

    def get_password_reset_token(self):
        return self._password_reset_token

    def get_password_reset_token_expiries(self):
        return self._password_reset_token_expiries

    def is_active(self):
        """Returns a value indicating whether this account is active.
        :return: True, if this account is active, False otherwise.
        :rtype: bool
        """
        return self._state == StateType.ACTIVE

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

    def set_role(self, newRole):
        self._role = newRole

    def set_name(self, newName):
        self._name = newName

    def set_state(self, new_state):
        self._state = new_state

    def generate_password_request_token(self):
        """Generats a new password reset token and sets the password token
        expiry date.
        :returns: The created token.
        :rtype: str"""
        self._password_reset_token = secrets.token_hex(33)
        self._password_reset_token_expiries = datetime.now() + timedelta(days=1)
        self._state = StateType.PASSWORT_RESET_PENDING

    def activate(self):
        """Activates the account if it is pending."""
        if self._state == StateType.ACTIVATION_PENDING:
            self._state = StateType.ACTIVE
