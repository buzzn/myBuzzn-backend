import json

from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from models.user import User, GenderType, StateType
from models.group import Group
from util.database import db

# pylint:disable=line-too-long
sample_avatar = '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'


class ProfileTestCase(BuzznTestCase):
    """Tests the login behavior"""

    def setUp(self):
        super().setUp()
        users_group = Group("SomeGroup", "group_meter_id",
                            '5e769d5b83934bccae11a8fa95e0dc5f', 'e2a7468f0cf64b7ca3f3d1350b893c6d')
        db.session.add(users_group)
        db.session.commit()
        self.target_user = User(GenderType.MALE, "Some", "User",
                                "user@some.net", "SomeToken", "SomeMeterId",
                                users_group.id)
        self.target_user.set_password("some_password")
        self.target_user.nick = "SomeNick"
        self.target_user.name = "SomeName"
        self.target_user.first_name = "SomeFirstName"
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
        self.assertEqual(response.json['name'], 'SomeName')
        self.assertEqual(response.json['firstName'], 'SomeFirstName')
        self.assertEqual(response.json['nick'], 'SomeNick')
        self.assertEqual(response.json['groupAddress'], 'SomeGroup')
        self.assertEqual(response.json['meterId'], 'SomeMeterId')

    def test_unknown_group(self):
        """Expect an empty string for group address if user is not member of any group.
        """
        user_no_group = User(GenderType.MALE, "Someother", "User2",
                             "user2@someother.net", "SomenewToken", "Meterid",
                             None)
        user_no_group.set_password("some_password")
        user_no_group.state = StateType.ACTIVE
        db.session.add(user_no_group)
        db.session.commit()

        login_request = self.client.post('/login',
                                         data=json.dumps(
                                             {'user': 'user2@someother.net',
                                              'password': 'some_password'}))

        response = self.client.get(
            '/profile',
            headers={'Authorization': 'Bearer {}'.format(
                login_request.json["sessionToken"])})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json['name'], 'User2')
        self.assertEqual(response.json['groupAddress'], '')

    def test_set_flat_size(self):
        """ Expect flatSize change if a new value is provided. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
                                                          'password': 'some_password'}))

        response = self.client.put(
            '/profile',
            headers={'Authorization': 'Bearer {}'.format(
                login_request.json["sessionToken"])},
            data=json.dumps({'flatSize': 33}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = User.query.filter_by(id=self.target_user.id).first()

        self.assertEqual(actual.flat_size, 33)

    def test_set_inhabitants(self):
        """ Expect inhabitants change if a new value is provided. """

        login_request = self.client.post('/login', data=json.dumps({'user': 'User@Some.net',
                                                                    'password': 'some_password'}))

        response = self.client.put(
            '/profile', headers={'Authorization': 'Bearer {}'.format(
                login_request.json["sessionToken"])},
            data=json.dumps({'inhabitants': 4}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = User.query.filter_by(id=self.target_user.id).first()

        self.assertEqual(actual.inhabitants, 4)

    def test_set_nick(self):
        """ Expect nick change if a new value is provided. """

        login_request = self.client.post('/login', data=json.dumps({'user': 'User@Some.net',
                                                                    'password': 'some_password'}))

        response = self.client.put(
            '/profile', headers={'Authorization': 'Bearer {}'.format(
                login_request.json["sessionToken"])},
            data=json.dumps({'nick': 'newNick'}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = User.query.filter_by(id=self.target_user.id).first()

        self.assertEqual(actual.nick, 'newNick')

    def test_set_avatar(self):
        """ Expect avatar change if a new value is provided. """

        login_request = self.client.post('/login', data=json.dumps({'user': 'User@Some.net',
                                                                    'password': 'some_password'}))

        response = self.client.put(
            '/profile', headers={'Authorization': 'Bearer {}'.format(
                login_request.json["sessionToken"])},
            data=json.dumps({'avatar': sample_avatar}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = User.query.filter_by(id=self.target_user.id).first()

        # The avatar is compressed and encoded as 200x200px image in the upload
        # process, so the return value cannot equal the original avatar
        self.assertTrue(len(actual.avatar) > 100)
