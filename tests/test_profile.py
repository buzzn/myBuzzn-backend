import json

from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from models.user import User, GenderType, StateType
from models.group import Group
from tests.string_constants import SAMPLE_AVATAR
from util.database import db


class ProfileTestCase(BuzznTestCase):
    """Tests the login behavior"""

    def setUp(self):

        db.drop_all()
        db.create_all()
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
            data=json.dumps({'avatar': SAMPLE_AVATAR}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        actual = User.query.filter_by(id=self.target_user.id).first()

        # The avatar is compressed and encoded as 200x200px image in the upload
        # process, so the return value cannot equal the original avatar
        self.assertTrue(len(actual.avatar) > 100)
