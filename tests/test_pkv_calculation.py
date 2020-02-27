from datetime import datetime
import json
from unittest import mock
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.pkv_calculation import define_base_values


SORTED_KEYS = [b'b4234cd4bed143a6b9bd09e347e17d34_2020-02-25 12:02:00',
               b'b4234cd4bed143a6b9bd09e347e17d34_2020-02-25 12:07:40',
               b'b4234cd4bed143a6b9bd09e347e17d34_2020-02-25 12:14:34']

USER_CONSUMPTION = [
    b'{"type": "reading", "values": {"energy": 18687322714815}}',
    b'{"type": "reading", "values": {"energy": 18687322714815}}',
    b'{"type": "reading", "values": {"energy": 18687322714815}}']

BASE_VALUES = {'date': datetime(2020, 2, 25).date(), 'consumption': 18687.322714815,
               'consumption_cumulated': 18687.322714815, 'inhabitants': 2,
               'pkv':  9343.6613574075, 'pkv_cumulated': 9343.6613574075,
               'days': 0, 'moving_average': 0.0, 'moving_average_annualized': 0}

PKV = {'date': datetime(2020, 2, 26).date(), 'consumption': 18687.322714815,
       'consumption_cumulated': 37356.64542963, 'inhabitants': 2,
       'pkv':  9343.6613574075, 'pkv_cumulated': 18687.322714815,
       'days': 1, 'moving_average': 9343.661357408, 'moving_average_annualized': 3410436}


class PKVCalculationTestCase(BuzznTestCase):
    """ Unit tests for PKV calculation methods. """

    def setUp(self):
        """ Create test user and test group in the database. """

        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', 'b4234cd4bed143a6b9bd09e347e17d34', 1)
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password')
        self.test_user.state = StateType.ACTIVE
        db.session.add(self.test_user)
        db.session.commit()
        self.client.post(
            '/login', data=json.dumps({'user': 'test@test.net', 'password': 'some_password'}))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION)
    def test_define_base_values(self, _get_meter_reading_date, _get):
        """ Unit tests for function define_base_values(). """

        start = datetime(2020, 2, 26).date()
        result = define_base_values(
            self.test_user.meter_id, self.test_user.inhabitants, start)

        # Check return type
        self.assertIsInstance(result, (dict, type(None)))

        # Check return values
        if isinstance(result, dict):
            for param in 'date', 'consumption', 'consumption_cumulated',\
                'inhabitants', 'pkv', 'pkv_cumulated', 'days', 'moving_average'\
                    'moving_average_annualized':
                self.assertEqual(result.get(param), BASE_VALUES.get(param))

    # pylint: disable=unused-argument
    # @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS)
    # @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION)
    def test_calc_pkv(self):  # , _get_meter_reading_date, _get):
        """ Unit tests for function calc_pkv(). """
