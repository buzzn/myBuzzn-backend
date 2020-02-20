import ast
import json
from unittest import mock
from flask_api import status
from models.user import User, GenderType, StateType
from models.group import Group
from models.user import User
from routes.group_profile_pictures import get_group_members
from tests.buzzn_test_case import BuzznTestCase
from tests.test_profile import sample_avatar
from util.database import db


DATA = [{'id': 1, 'avatar': sample_avatar},
        {'id': 2, 'avatar': sample_avatar},
        {'id': 3, 'avatar': sample_avatar}]


class GroupProfilePictures(BuzznTestCase):
    """ Unit tests for group profile pictures. """

    def setUp(self):
        super().setUp()
        db.session.add(Group('TestGroup', '269e682dbfd74a569ff4561b6416c999'))
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net', 'TestToken',
                         'b4234cd4bed143a6b9bd09e347e17d34', 1)
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        group_member2 = User(GenderType.FEMALE, 'judith', 'greif',
                             'judith@buzzn.net', 'TestToken2',
                             '52d7c87f8c26433dbd095048ad30c8cf', 1)
        group_member2.set_password('some_password2')
        group_member2.state = StateType.ACTIVE
        group_member3 = User(GenderType.MALE, 'danny', 'stey',
                             'danny@buzzn.net', 'TestToken3',
                             '117154df05874f41bfdaebcae6abfe98', 1)
        group_member3.set_password('some_password3')
        group_member3.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.add(group_member2)
        db.session.add(group_member3)
        db.session.commit()
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
                                                          'password': 'some_password'}))
        self.client.put('/profile',
                        headers={'Authorization': 'Bearer {}'.format(
                            login_request.json["sessionToken"])},
                        data=json.dumps({'nick': 'newNick',
                                         'flatSize': 33.0,
                                         'inhabitants': 2,
                                         'avatar': sample_avatar}))
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'judith@buzzn.net',
                                                          'password': 'some_password2'}))
        self.client.put('/profile',
                        headers={'Authorization': 'Bearer {}'.format(
                            login_request.json["sessionToken"])},
                        data=json.dumps({'nick': 'newNick',
                                         'flatSize': 34.0,
                                         'inhabitants': 3,
                                         'avatar': sample_avatar}))
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'danny@buzzn.net',
                                                          'password':
                                                          'some_password3'}))
        self.client.put('/profile',
                        headers={'Authorization': 'Bearer {}'.format(
                            login_request.json["sessionToken"])},
                        data=json.dumps({'nick': 'newNick',
                                         'flatSize': 35.0,
                                         'inhabitants': 4,
                                         'avatar': sample_avatar}))

    def test_get_group_members(self):
        """ Unit tests for function get_group_members(). """

        result = get_group_members(1)

        # Check result types
        self.assertIsInstance(result, list)
        for group_member in result:
            self.assertIsInstance(group_member, dict)
            self.assertIsInstance(group_member.get('id'), int)
            self.assertIsInstance(group_member.get('avatar'), bytes)

            # Check result values
            self.assertTrue(len(group_member['avatar']) > 100)

    # pylint: disable=unused-argument
    @mock.patch('routes.group_profile_pictures.get_group_members',
                return_value=DATA)
    def test_group_profile_pictures(self, _get_group_members):
        """ Unit tests for group_profile_pictures(). """

        # Check if route exists
        login_request = self.client.post('/login', data=json.dumps({'user':
                                                                    'test@test.net',
                                                                    'password':
                                                                    'some_password'}))
        response = self.client.get('/assets/group-profile-pictures',
                                   headers={'Authorization': 'Bearer {}'.
                                                             format(login_request.json
                                                                    ["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertIsInstance(response.data, bytes)
        self.assertEqual(ast.literal_eval(response.data.decode('utf-8')), DATA)