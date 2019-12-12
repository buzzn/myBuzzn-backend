import json

from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from models.user import User, GenderType, StateType
from util.database import db

class ProfileTestCase(BuzznTestCase):
    """Tests the login behavior"""

    def setUp(self):
        super().setUp()

        self.target_user = User(GenderType.MALE, "SomeUser", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        db.session.add(self.target_user)
        db.session.commit()

    def test_get_profile(self):
        """Expect HTTP_200_OK if a user requests his profile.
        """
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
                                                          'password': 'some_password'}))

        response = self.client.get(
            '/profile',
            headers={'Authorization': 'Bearer {}'.format(
                login_request.json["sessionToken"])})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json['name'], 'SomeUser')

    def test_set_profile(self):
        """Expect a change in the profile if a new one is provided.
        """
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
                                                          'password': 'some_password'}))

        response = self.client.put(
            '/profile',
            headers={'Authorization': 'Bearer {}'.format(login_request.json["sessionToken"])},
            data=json.dumps({'name': 'NewName',
                             'flatSize': 33,
                             'inhabitants': 4}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = User.query.filter_by(id=self.target_user.id).first()

        self.assertEqual(actual.flat_size, 33)
        self.assertEqual(actual.inhabitants, 4)
        self.assertEqual(actual.name, 'NewName')
