from unittest import mock
from tests.buzzn_test_case import BuzznTestCase
from websocket import Websocket

METER_ID = 'b4234cd4bed143a6b9bd09e347e17d34'
GROUP_METER_ID = '269e682dbfd74a569ff4561b6416c999'
USER_ID = 3
GROUP_METER_IDS = [{"id": 1, "meter_id": '52d7c87f8c26433dbd095048ad30c8cf'},
                   {"id": 2, "meter_id": '117154df05874f41bfdaebcae6abfe98'}]
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
    "groupConsumption": 3520150977541000,
    "groupProduction": 0,
    "selfSufficiency": 0.5,
    "usersConsumption": [{"id": 3, "consumption": 1931131646000},
                         {"id": 1, "consumption": 186720209342000},
                         {"id": 2, "consumption": 1490956772802000}]
}


class WebsocketTestCase(BuzznTestCase):
    """ Unit tests for class Websocket. """

    @mock.patch('flask_socketio.SocketIO')
    @mock.patch('discovergy.discovergy.Discovergy.get_last_reading',
                side_effect=[GROUP_LAST_READING, INDIVIDUAL_LAST_READING,
                             GROUPMEMBER1_LAST_READING,
                             GROUPMEMBER2_LAST_READING])
    def test_create_data(self, socketio, get_last_reading):
        """ Unit tests for function create_data(). """

        # websocket = Websocket()
        # Check return type

        # Check return value
