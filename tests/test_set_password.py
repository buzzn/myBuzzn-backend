import json

from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from models.user import User, GenderType
from routes.set_password import Errors
from util.database import db


class SetPasswordTest(BuzznTestCase):
    """Checks if users can be created."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.add(User(GenderType.MALE, "Some", "User", "User@Some.net",
                            "SomeToken", "SomeMeterId", "SomeGroup"))
        db.session.commit()

    def test_user_does_not_exist(self):
        """Expect an error on a set password request for a not existing user
        name"""
        response = self.client.post(
            '/set-password', data=json.dumps({'user': 'Other_User@Some.net',
                                              'token': 'SomeOtherToken',
                                              'password': 'SomePassword'}))
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json, Errors.UNKNOWN_USER.__dict__)

    def test_token_does_not_match(self):
        """Expect an error if a set password request is called with a not
        existing token."""
        response = self.client.post('/set-password', data=json.dumps({
            'user': 'User@Some.net',
            'token': 'Wrong token',
            'password': 'SomePassword'
        }))
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json, Errors.WRONG_TOKEN.__dict__)

    def test_no_activation_pending(self):
        """Expect an error if an account is activated for the seconds time."""
        response = self.client.post('/set-password', data=json.dumps({
            'user': 'User@Some.net',
            'token': 'SomeToken',
            'password': 'SomePassword'
        }))

        # First time should be alright
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

        # Let's do this again
        response = self.client.post('/set-password', data=json.dumps({
            'user': 'User@Some.net',
            'token': 'SomeToken',
            'password': 'SomePassword'
        }))
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json, Errors.NO_ACTIVATION_PENDING.__dict__)

    def test_correct_data_should_set_password(self):
        """Check whether correctly provided parameters do activate an account
        """
        response = self.client.post('/set-password', data=json.dumps({
            'user': 'User@Some.net',
            'token': 'SomeToken',
            'password': 'SomePassword'
        }))
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
