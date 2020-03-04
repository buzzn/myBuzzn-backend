from datetime import datetime
import json
from unittest import mock
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.pkv_calculation import define_base_values, calc_pkv,\
    get_first_meter_reading_date


SORTED_KEYS = [b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-25 12:02:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-25 12:07:40',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-25 12:14:34']

USER_CONSUMPTION = [
    b'{"type": "reading", "values": {"energy": 198360858657000}}',
    b'{"type": "reading", "values": {"energy": 198370000000000}}',
    b'{"type": "reading", "values": {"energy": 198382608371000}}']

USER_CONSUMPTION_TWICE = USER_CONSUMPTION + USER_CONSUMPTION

BASE_VALUES = {'date': datetime(2020, 2, 25).date(), 'consumption': 0.0,
               'consumption_cumulated': 0.0, 'inhabitants': 2, 'pkv': 0.0,
               'pkv_cumulated': 0.0, 'days': 0, 'moving_average': 0.0,
               'moving_average_annualized': 0}

PKV_DAY_ONE = {'date': datetime(2020, 2, 25).date(), 'consumption': 21.749714,
               'consumption_cumulated': 21.749714, 'inhabitants': 2,
               'pkv':  10.874857, 'pkv_cumulated': 10.874857,
               'days': 1, 'moving_average': 10.874857, 'moving_average_annualized': 3969}


class PKVCalculationTestCase(BuzznTestCase):
    """ Unit tests for PKV calculation methods. """

    def setUp(self):
        """ Create test user and test group in the database. """

        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', '52d7c87f8c26433dbd095048ad30c8cf', 1)
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password')
        self.test_user.state = StateType.ACTIVE
        db.session.add(self.test_user)
        db.session.commit()
        self.client.post(
            '/login', data=json.dumps({'user': 'test@test.net', 'password': 'some_password'}))

    def test_define_base_values(self):
        """ Unit tests for function define_base_values(). """

        start = datetime(2020, 2, 26).date()
        result = define_base_values(self.test_user.inhabitants, start)

        # Check return type
        self.assertIsInstance(result, (dict, type(None)))

        # Check return values
        if isinstance(result, dict):
            for param in 'date', 'consumption', 'consumption_cumulated',\
                'inhabitants', 'pkv', 'pkv_cumulated', 'days', 'moving_average'\
                    'moving_average_annualized':
                self.assertEqual(result.get(param), BASE_VALUES.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_TWICE)
    def test_calc_pkv(self, _get_meter_reading_date, _get):
        """ Unit tests for function calc_pkv(). """

        start = datetime(2020, 2, 25).date()
        result = calc_pkv(
            self.test_user.meter_id, self.test_user.inhabitants, start)

        # Check result type
        self.assertIsInstance(result, (dict, type(None)))

        # Check result values
        if isinstance(result, dict):
            for param in 'date', 'consumption', 'consumption_cumulated',\
                         'inhabitants', 'pkv', 'pkv_cumulated', 'days',\
                         'moving_average', 'moving_average_annualized':
                self.assertEqual(result.get(param), PKV_DAY_ONE.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION)
    def test_get_first_meter_reading_date(self, scan_iter, get):
        """ Unit tests for function get_first_meter_reading_date() """

        start = datetime(2020, 2, 25).date()
        result = get_first_meter_reading_date(self.test_user.meter_id, start)

        # Check result types
        self.assertIsInstance(result, (int, type(None)))
