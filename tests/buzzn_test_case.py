import bcrypt

from flask_testing import TestCase
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
    """Creates app configured to run buzzn tests."""
    def setUp(self):
        db.drop_all()
        db.create_all()

    def create_app(self):
        app = setup_app(TestConfig())
        return app
