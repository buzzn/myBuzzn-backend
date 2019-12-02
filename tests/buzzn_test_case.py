from flask_testing import TestCase
from setup_app import setup_app


class TestConfig():
    """The config to be used in the test cases"""
    SECRET_KEY = 'testingkey'
    TESTING = True
    LIVESERVER_PORT = 0
    CLIENT_NAME = 'BuzznClient'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class BuzznTestCase(TestCase):
    """Creates app configured to run buzzn tests."""

    def create_app(self):
        app = setup_app(TestConfig())
        return app
