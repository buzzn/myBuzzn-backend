import json
from unittest import mock
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.websocket_provider import WebsocketProvider, get_parameters


GROUP_LAST_READING = {
    'time': 1575539067000,
    'values': {
        'power': 20420100,
        'power3': 6928720,
        'energyOut': 0,
        'power1': 6563800,
        'energy': 3520052364335000,
        'power2': 6927580
    }
}
INDIVIDUAL_FIRST_READING = [{
    'time': 1572994800000,
    'values': {
        'energyOut': 2189063000,
        'energy2': 0, 'energy1': 0,
        'voltage1': 231842,
        'voltage2': 231242,
        'voltage3': 231525,
        'energyOut1': 0,
        'power': 35118,
        'energyOut2': 0,
        'power3': 454,
        'power1': 12045,
        'energy': 1738297570859,
        'power2': 22557
    }
}]
INDIVIDUAL_LAST_READING = {
    'time': 1575539517430,
    'values': {
        'energyOut': 2189063000,
        'energy2': 0,
        'energy1': 0,
        'voltage1': 233100,
        'voltage2': 233500,
        'voltage3': 233200,
        'energyOut1': 0,
        'power': 21130,
        'energyOut2': 0,
        'power3': 0,
        'power1': 1390,
        'energy': 1931041534000,
        'power2': 19740
    }
}
GROUPMEMBER1_LAST_READING = {
    'time': 1575542671508,
    'values': {
        'power': 366870,
        'power3': 154420,
        'energyOut': 0,
        'power1': 144000,
        'energy': 186728851677000,
        'power2': 68450
    }
}
GROUPMEMBER2_LAST_READING = {
    'time': 1575542670918,
    'values': {
        'power': 11156280,
        'power3': 3693230,
        'energyOut': 0,
        'power1': 3760540,
        'energy': 1491013650297000,
        'power2': 3702510
    }
}
DATA = {
    "date": 1575540829887,
    "groupConsumption": 3520052364335000,
    "groupProduction": 0,
    "selfSufficiency": 6.225875925992823e-10,
    "usersConsumption": [{"id": 1, "consumption": 1931041534000},
                         {"id": 2, "consumption": 186728851677000},
                         {"id": 3, "consumption": 1491013650297000}]
}
RETURN_VALUES = [GROUP_LAST_READING, INDIVIDUAL_LAST_READING,
                 GROUPMEMBER1_LAST_READING, GROUPMEMBER2_LAST_READING]
SELF_SUFFICIENCY = 6.225875925992823e-10
GROUP_MEMBERS = [{'id': 2, 'meter_id': '52d7c87f8c26433dbd095048ad30c8cf'}, {
    'id': 3, 'meter_id': '117154df05874f41bfdaebcae6abfe98'}]
METER_ID = 'b4234cd4bed143a6b9bd09e347e17d34'
GROUP_METER_ID = '269e682dbfd74a569ff4561b6416c999'
INHABITANTS = 2
FLAT_SIZE = 60.0


class WebsocketProviderTestCase(BuzznTestCase):
    """ Unit tests for class WebsocketProvider. """

    def setUp(self):
        """ Create a test user and a test group in the test database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'TestUser', 'test@test.net', 'TestToken',
                         'b4234cd4bed143a6b9bd09e347e17d34', 1)
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.add(User(GenderType.FEMALE, 'judith', 'judith@buzzn.net',
                            'TestToken2', '52d7c87f8c26433dbd095048ad30c8cf',
                            1))
        db.session.add(User(GenderType.MALE, 'danny', 'danny@buzzn.net',
                            'TestToken3', '117154df05874f41bfdaebcae6abfe98', 1))
        db.session.add(Group('TestGroup',
                             '269e682dbfd74a569ff4561b6416c999'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('discovergy.discovergy.Discovergy')
    @mock.patch('discovergy.discovergy.Discovergy.login')
    @mock.patch('discovergy.discovergy.Discovergy.get_last_reading',
                side_effect=RETURN_VALUES)
    @mock.patch('util.websocket_provider.WebsocketProvider.self_sufficiency',
                return_value=SELF_SUFFICIENCY)
    # pylint: disable=too-many-arguments
    def test_create_data(self, socketio, discovergy, login, get_last_reading, self_sufficiency):
        """ Unit tests for function create_data(). """

        ws = WebsocketProvider()
        test_user = db.session.query(
            User).filter_by(name='TestUser').first()
        data = ws.create_data(test_user.id)

        # Check return type
        self.assertTrue(isinstance(data, dict))

        # Check return values
        for param in 'groupConsumption', 'groupProduction', 'selfSufficiency':
            self.assertEqual(data.get(param), DATA.get(param))
        for item1, item2 in zip(data.get('usersConsumption'),
                                DATA.get('usersConsumption')):
            self.assertEqual(item1.get('id'), item2.get('id'))
            self.assertEqual(item1.get('consumption'),
                             item2.get('consumption'))

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('discovergy.discovergy.Discovergy')
    @mock.patch('discovergy.discovergy.Discovergy.login')
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=INDIVIDUAL_FIRST_READING)
    @mock.patch('discovergy.discovergy.Discovergy.get_last_reading',
                return_value=INDIVIDUAL_LAST_READING)
    # pylint: disable=too-many-arguments
    def test_self_sufficiency(self, socketio, discovergy, login, get_readings, get_last_reading):
        """ Unit tests for function self_sufficiency(). """

        ws = WebsocketProvider()
        test_user = db.session.query(
            User).filter_by(name='TestUser').first()
        meter_id = test_user.meter_id
        self_sufficiency = ws.self_sufficiency(
            meter_id, test_user.inhabitants, test_user.flat_size)

        # Check return type
        self.assertTrue(isinstance(self_sufficiency, float))

        # Check return value
        # self.assertEqual(self_sufficiency, SELF_SUFFICIENCY)

    def test_get_parameters(self):
        """ Unit tests for function get_parameters(). """

        result = get_parameters(1)

        # Check result values
        self.assertEqual(result[0], METER_ID)
        self.assertEqual(result[1], GROUP_METER_ID)
        self.assertEqual(result[2], GROUP_MEMBERS)
        self.assertEqual(result[3], INHABITANTS)
        self.assertEqual(result[4], FLAT_SIZE)

        # Check result type
        self.assertTrue(isinstance(result, tuple))
