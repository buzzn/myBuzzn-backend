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
    PASSWORD_SALT = bcrypt.gensalt()


class BuzznTestCase(TestCase):
    """Creates apps configures to run buzzn tests."""
    def setUp(self):
        db.create_all()

    def create_app(self):
        app = setup_app(TestConfig())
        return app
