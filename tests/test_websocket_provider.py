import json
from unittest import mock
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.websocket_provider import WebsocketProvider, get_group_meter_id,\
    get_group_members


GROUP_LAST_READING = {'type': 'reading',
                      'values': {'energyOut': 2189063000, 'energy2': 0,
                                 'energy1': 0, 'voltage1': 231000,
                                 'voltage2': 231900, 'voltage3': 231500,
                                 'energyOut1': 0, 'power': 21520,
                                 'energyOut2': 0, 'power3': 0, 'power1': 1700,
                                 'energy': 2466839634000, 'power2': 19820}}
GROUPMEMBER1_LAST_READING = {'type': 'reading',
                             'values': {'power': 20032100, 'power3': -2730,
                                        'energyOut': 0, 'power1': -173960,
                                        'energy': 3603609657330000, 'power2': -5900}}
GROUPMEMBER2_LAST_READING = {'type': 'reading',
                             'values': {'power': 734100, 'power3': 35180,
                                        'energyOut': 0, 'power1': 125670,
                                        'energy': 190585532038000, 'power2': 26720}}
GROUPMEMBER3_LAST_READING = {'type': 'reading',
                             'values': {'power': 5877540, 'power3': 1361800,
                                        'energyOut': 0, 'power1': 1410390,
                                        'energy': 1500976759905000, 'power2': 1388390}}
DATA = {"date": 1582102636258,
        "group_consumption": 2466839634000,
        "group_production": 2189063000,
        "group_users": [{"id": 1, "meter_id": "b4234cd4bed143a6b9bd09e347e17d34",
                         "consumption": 3603609657330000, "power": 20032100,
                         "self_sufficiency": 1.1093780095648228e-13},
                        {"id": 2, "meter_id": "52d7c87f8c26433dbd095048ad30c8cf",
                         "consumption": 190585532038000, "power": 734100,
                         "self_sufficiency": 1.2037243127210752e-12},
                        {"id": 3, "meter_id": "117154df05874f41bfdaebcae6abfe98",
                         "consumption": 1500976759905000, "power": 5877540,
                         "self_sufficiency": 1.5915618042558239e-13}]}
RETURN_VALUES = [GROUPMEMBER1_LAST_READING,
                 GROUPMEMBER2_LAST_READING, GROUPMEMBER3_LAST_READING]
SELF_SUFFICIENCIES = [1.1093780095648228e-13,
                      1.2037243127210752e-12,
                      1.5915618042558239e-13]
GROUPMEMBER1_FIRST_READING = {'type': 'reading',
                              'values': {'power': 13374273, 'power3': 3902020,
                                         'energyOut': 0, 'power1': 3565876,
                                         'energy': 3055907952664000, 'power2': 4029106}}
GROUP_MEMBERS = [{'id': 1, 'meter_id': 'b4234cd4bed143a6b9bd09e347e17d34',
                  'inhabitants': 2, 'flat_size': 60.0},
                 {'id': 2, 'meter_id': '52d7c87f8c26433dbd095048ad30c8cf',
                  'inhabitants': 2, 'flat_size': 60.0},
                 {'id': 3, 'meter_id': '117154df05874f41bfdaebcae6abfe98',
                  'inhabitants': 2, 'flat_size': 60.0}]
GROUP_METER_ID = '269e682dbfd74a569ff4561b6416c999'
SELF_SUFFICIENCY = 2.1909736445530789e-13
MEMBER_DATA = [{'id': 1, 'meter_id': 'b4234cd4bed143a6b9bd09e347e17d34',
                'consumption': 3603609657330000, 'power': 20032100,
                'self_sufficiency': 1.1093780095648228e-13},
               {'id': 2, 'meter_id': '52d7c87f8c26433dbd095048ad30c8cf',
                'consumption': 190585532038000, 'power': 734100,
                'self_sufficiency': 1.2037243127210752e-12},
               {'id': 3, 'meter_id': '117154df05874f41bfdaebcae6abfe98',
                'consumption': 1500976759905000, 'power': 5877540,
                'self_sufficiency': 1.5915618042558239e-13}]


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
        test_user.set_password('some_password')
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
                             '269e682dbfd74a569ff4561b6416c999'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))

    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('util.websocket_provider.WebsocketProvider.get_last_reading',
                side_effect=RETURN_VALUES)
    @mock.patch('util.websocket_provider.WebsocketProvider.self_sufficiency',
                side_effect=SELF_SUFFICIENCIES)
    def test_create_member_data(self, socketio, _get_last_reading,
                                _self_sufficiency):
        """ Unit tests for function create_member_data(). """

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('util.websocket_provider.WebsocketProvider.get_last_reading',
                return_value=GROUP_LAST_READING)
    @mock.patch('util.websocket_provider.WebsocketProvider.create_member_data',
                side_effect=MEMBER_DATA)
    def test_create_data(self, socketio, get_last_reading, _create_member_data):
        """ Unit tests for function create_data(). """

        ws = WebsocketProvider()
        test_user = db.session.query(
            User).filter_by(name='User').first()
        data = ws.create_data(test_user.id)

        # Check return type
        self.assertTrue(isinstance(data, dict))

        # Check return values
        for param in 'group_consumption', 'group_production':
            self.assertEqual(data.get(param), DATA.get(param))
        for item1, item2 in zip(data.get('group_users'), DATA.get('group_users')):
            self.assertEqual(item1.get('id'), item2.get('id'))
            self.assertEqual(item1.get('meter_id'), item2.get('meter_id'))
            self.assertEqual(item1.get('consumption'),
                             item2.get('consumption'))
            self.assertEqual(item1.get('power'),
                             item2.get('power'))
        #     self.assertEqual(item1.get('self_sufficiency'),
        #                      item2.get('self_sufficiency'))

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('util.websocket_provider.WebsocketProvider.get_last_reading',
                return_value=GROUPMEMBER1_LAST_READING)
    @mock.patch('util.websocket_provider.WebsocketProvider.get_first_reading',
                return_value=GROUPMEMBER1_FIRST_READING)
    def test_self_sufficiency(self, socketio, get_last_reading,
                              get_first_reading):
        """ Unit tests for function self_sufficiency(). """

        ws = WebsocketProvider()
        test_user = db.session.query(
            User).filter_by(name='User').first()
        meter_id = test_user.meter_id
        self_sufficiency = ws.self_sufficiency(
            meter_id, test_user.inhabitants, test_user.flat_size)

        # Check return type
        self.assertTrue(isinstance(self_sufficiency, float))

        # Check return value
        self.assertEqual(self_sufficiency, SELF_SUFFICIENCY)

    def test_get_group_meter_id(self):
        """ Unit tests for function get_group_meter_id(). """

        result = get_group_meter_id(1)

        # Check result values
        self.assertEqual(result, GROUP_METER_ID)

        # Check result type
        self.assertIsInstance(result, str)

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
            self.assertIsInstance(group_user.get('flat_size'), float)

            # Check result values
            self.assertEqual(
                group_user, GROUP_MEMBERS[result.index(group_user)])
