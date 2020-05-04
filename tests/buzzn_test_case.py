import bcrypt

from flask_testing import TestCase
from models.group import Group
from models.user import User, GenderType, StateType, BaselineStateType
from setup_app import setup_app
from util.database import db


class TestConfig():
    """The config to be used in the test cases"""
    SECRET_KEY = 'testingkey'
    TESTING = True
    LIVESERVER_PORT = 0
    CLIENT_NAME = 'BuzznClient'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PASSWORD_SALT = bcrypt.gensalt().hex()
    BUZZN_SMTP_SERVER = 'BUZZN_SMTP_SERVER'
    BUZZN_SMTP_SERVER_PORT = '456'
    BUZZN_EMAIL = 'team@buzzn.net'
    BUZZN_EMAIL_PASSWORD = 'BUZZN_EMAIL_PASSWORD'
    BUZZN_BASE_URL = 'localhost:5000'
    BUZZN_MAILER = 'stdout'


class BuzznTestCase(TestCase):
    """ Creates app configured to run buzzn tests. """

    def setUp(self):
        """ Sets up a fresh database, creates a test user and a test group. """

        db.drop_all()
        db.create_all()
        self.test_case_user = User(GenderType.MALE, 'Some', 'User',
                                   'test@test.net', 'TestToken',
                                   'EASYMETER_60404854', 1)
        self.test_case_user.flat_size = 60.0
        self.test_case_user.inhabitants = 2
        self.test_case_user.set_password('some_password')
        self.test_case_user.state = StateType.ACTIVE
        self.test_case_user.baseline_state = BaselineStateType.READY
        db.session.add(self.test_case_user)
        self.test_case_group = Group(
            "SomeGroup",
            'EASYMETER_1124001747',
            '5e769d5b83934bccae11a8fa95e0dc5f',
            'e2a7468f0cf64b7ca3f3d1350b893c6d')
        db.session.add(self.test_case_user)
        db.session.add(self.test_case_group)
        db.session.commit()

    def create_app(self):
        app = setup_app(TestConfig())
        return app
