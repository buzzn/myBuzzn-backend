import json

from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from models.user import User, GenderType, StateType
from util.database import db

class LoginTestCase(BuzznTestCase):
    """Tests the login behavior"""

    def setUp(self):
        super().setUp()

        self.target_user = User(GenderType.MALE, "Some", "User", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        db.session.add(self.target_user)
        db.session.commit()

    def test_valid_credentials(self):
        """Expect HTTP_200_OK if an existing valid user tries to login
        """
        response = self.client.post('/login',
                                    data=json.dumps({'user': 'User@Some.net',
                                                     'password': 'some_password'}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_password(self):
        """Expect HTTP_401_UNAUTHORIZED on login attempt using invalid password.
        """
        response = self.client.post('/login',
                                    data=json.dumps({'user': 'User@Some.net',
                                                     'password': 'invalidpass'}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_exsisting_user(self):
        """Expect HTTP_401_UNAUTHORIZED on login attempt using non existing user.
        """
        response = self.client.post('/login',
                                    data=json.dumps({'user': 'other_user@Some.net',
                                                     'password': 'some_password'}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivated_user(self):
        """Expect HTTP_403_FORBIDDEN on login attempt using a deactivated user account.
        """
        self.target_user.state = StateType.DEACTIVATED
        db.session.commit()
        response = self.client.post('/login',
                                    data=json.dumps({'user': 'User@Some.net',
                                                     'password': 'some_password'}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
