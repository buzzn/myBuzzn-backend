from flask_testing import TestCase

from setup_app import setup_app


class TestConfig():
    """The config to be used in the test cases"""
    SECRET_KEY = 'testingkey'
    TESTING = True
    LIVESERVER_PORT = 0


class BuzznTestCase(TestCase):
    """Creates apps configures to run buzzn tests."""

    def create_app(self):
        config = TestConfig()
        return setup_app(config)
