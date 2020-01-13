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
    DEACTIVATED = 'User account is deactivated'

# Maybe setters should not count as public.
#pylint: disable=too-many-public-methods
class User(db.Model):
    """Represents a user account in the backend.
    """
    @staticmethod
    def NAME_MAX_LENGTH():
        return User.name.property.columns[0].type.length

    @staticmethod
    def PASSWORD_MAX_LENGTH():
        return User.password.property.columns[0].type.length

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

    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Enum(GenderType))
    first_name = db.Column(db.String(33))
    name = db.Column(db.String(33))
    nick = db.Column(db.String(33))
    mail = db.Column(db.String(33))
    activation_token = db.Column(db.String(33), unique=True)
    password = db.Column(db.String(333))
    state = db.Column(db.Enum(StateType))
    role = db.Column(db.Enum(RoleType))
    meter_id = db.Column(db.String(32))
    inhabitants = db.Column(db.Integer)
    flat_size = db.Column(db.Float)
    group_id = db.Column(db.Integer, ForeignKey('group.id'))
    password_reset_token = db.Column(db.String(33), unique=True)
    password_reset_token_expires = db.Column(db.DateTime)
    avatar = db.Column(db.LargeBinary)

    # Plain value constructor, too many arguments is ok here
    #pylint: disable=too-many-arguments
    def __init__(self, gender, first_name, name, mail, activation_token, meter_id, group_id):
        """Creates a new user account and sets its state to pending.
        :param gender: The user's gender.
        :param str name: The user's name.
        :param str name: The user's mail address.
        :param str activation_token: Token to activate the account.
        :param str meter_id: the user's meter id
        :param int group_id: the user's group id
        """
        self.gender = gender
        self.first_name = first_name
        self.name = name
        self.mail = mail.lower()
        self.activation_token = activation_token
        self.state = StateType.ACTIVATION_PENDING
        self.role = RoleType.LOCAL_POWER_TAKER
        self.meter_id = meter_id
        self.group_id = group_id

    def is_active(self):
        """Returns a value indicating whether this account is active.
        :return: True, if this account is active, False otherwise.
        :rtype: bool
        """
        return self.state == StateType.ACTIVE

    def check_password(self, password_to_check):
        """Checks whether the given password matches the user's.
        :param str password_to_check: Password in plaintext.
        :return: True if the passwort matches, False otherwise.
        :rtype: bool
        """
        return bcrypt.checkpw(password_to_check.encode('utf-8'),
                              self.password)

    def set_password(self, newPassword):
        """Sets the user's password.
        :param self:
        :param newPassword: The new password in plaintext.
        """
        self.password = User.generate_password_hash(newPassword)

    def set_role(self, newRole):
        self.role = newRole

    def set_name(self, newName):
        self.name = newName

    def set_state(self, new_state):
        self.state = new_state

    def generate_password_request_token(self):
        """Generats a new password reset token and sets the password token
        expiry date.
        :returns: The created token.
        :rtype: str"""
        self.password_reset_token = secrets.token_hex(33)
        self.password_reset_token_expires = datetime.now() + timedelta(days=1)
        self.state = StateType.PASSWORT_RESET_PENDING

    def activate(self):
        """Activates the account if it is pending."""
        if self.state == StateType.ACTIVATION_PENDING:
            self.state = StateType.ACTIVE
