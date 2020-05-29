import json
from unittest import mock
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import GROUP_LAST_READING, GROUP_MEMBERS, GROUP_PRODUCTION_METER_IDS,\
    GROUPMEMBER1_LAST_READING, GROUPMEMBER1_WEBSOCKET_DATA, MEMBER_WEBSOCKET_DATA, WEBSOCKET_DATA
from util.database import db
from util.websocket_provider import WebsocketProvider, get_group_production_meter_ids,\
    get_group_members


class WebsocketProviderTestCase(BuzznTestCase):
    """ Unit tests for class WebsocketProvider. """

    def setUp(self):
        """ Create a test user and a test group in the test database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net', 'TestToken',
                         'b4234cd4bed143a6b9bd09e347e17d34', 1)
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password1')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        test_user2 = User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                          'TestToken2', '52d7c87f8c26433dbd095048ad30c8cf',
                          1)
        test_user2.flat_size = 60.0
        test_user2.inhabitants = 2
        db.session.add(test_user2)
        test_user3 = User(GenderType.MALE, 'danny', 'stey', 'danny@buzzn.net',
                          'TestToken3', '117154df05874f41bfdaebcae6abfe98', 1)
        test_user3.flat_size = 60.0
        test_user3.inhabitants = 2
        db.session.add(test_user3)
        db.session.add(Group('TestGroup',
                             '269e682dbfd74a569ff4561b6416c999',
                             '5e769d5b83934bccae11a8fa95e0dc5f',
                             'e2a7468f0cf64b7ca3f3d1350b893c6d'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password1'}))

    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('util.websocket_provider.WebsocketProvider.get_last_reading',
                return_value=GROUPMEMBER1_LAST_READING)
    def test_create_member_data(self, socketio, _get_last_reading):
        """ Unit tests for function create_member_data(). """

        ws = WebsocketProvider()
        test_user = db.session.query(
            User).filter_by(name='User').first()
        group_members = get_group_members(test_user.id)

        data = ws.create_member_data(group_members[0])

        # Check return type
        self.assertTrue(isinstance(data, dict))

        # Check return values
        for param in 'id', 'meter_id', 'consumption', 'power':
            self.assertEqual(
                data.get(param), GROUPMEMBER1_WEBSOCKET_DATA.get(param))

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('util.websocket_provider.WebsocketProvider.get_last_reading',
                return_value=GROUP_LAST_READING)
    @mock.patch('util.websocket_provider.WebsocketProvider.create_member_data',
                side_effect=MEMBER_WEBSOCKET_DATA)
    def test_create_data(self, socketio, get_last_reading, _create_member_data):
        """ Unit tests for function create_data(). """

        ws = WebsocketProvider()
        test_user = db.session.query(
            User).filter_by(name='User').first()
        data = ws.create_data(test_user.id)

        # Check return type
        self.assertTrue(isinstance(data, dict))

        # Check return values
        self.assertEqual(data.get('group_production'),
                         WEBSOCKET_DATA.get('group_production'))
        for item1, item2 in zip(data.get('group_users'), WEBSOCKET_DATA.get('group_users')):
            self.assertEqual(item1.get('id'), item2.get('id'))
            self.assertEqual(item1.get('meter_id'), item2.get('meter_id'))
            self.assertEqual(item1.get('consumption'),
                             item2.get('consumption'))
            self.assertEqual(item1.get('power'), item2.get('power'))

    def test_get_group_production_meter_ids(self):
        """ Unit tests for function get_group_production_meter_ids(). """

        result = get_group_production_meter_ids(1)

        # Check result values
        self.assertEqual(result, GROUP_PRODUCTION_METER_IDS)

        # Check result type
        self.assertIsInstance(result, tuple)

    def test_get_group_members(self):
        """ Unit tests for function get_group_members(). """

        result = get_group_members(1)

        # Check result types
        self.assertIsInstance(result, list)
        for group_user in result:
            self.assertIsInstance(group_user, dict)
            self.assertIsInstance(group_user.get('id'), int)
            self.assertIsInstance(group_user.get('meter_id'), str)
            self.assertIsInstance(group_user.get('inhabitants'), int)

            # Check result values
            self.assertEqual(
                group_user, GROUP_MEMBERS[result.index(group_user)])
