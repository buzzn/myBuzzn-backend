from datetime import datetime, timedelta
import json
from unittest import mock, skip
from sqlalchemy.engine.result import RowProxy
from models.pkv import PKV
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.pkv_calculation import define_base_values, calc_pkv,\
    get_first_meter_reading_date, check_input_parameter_date,\
    get_data_day_before


SORTED_KEYS_DAY_ONE = [b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-25 12:02:00',
                       b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-25 12:07:40',
                       b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-25 12:14:34']

SORTED_KEYS_DAY_TWO = [b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-26 12:02:00',
                       b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-26 12:07:40',
                       b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-26 12:14:34']

USER_CONSUMPTION_DAY_ONE = [
    b'{"type": "reading", "values": {"energy": 198360858657000}}',
    b'{"type": "reading", "values": {"energy": 198370000000000}}',
    b'{"type": "reading", "values": {"energy": 198382608371000}}']

USER_CONSUMPTION_DAY_TWO = [
    b'{"type": "reading", "values": {"energy": 198385000000000}}',
    b'{"type": "reading", "values": {"energy": 198390000000000}}',
    b'{"type": "reading", "values": {"energy": 198400000000000}}']

USER_CONSUMPTION_DAY_ONE_TWICE = USER_CONSUMPTION_DAY_ONE +\
    USER_CONSUMPTION_DAY_ONE

USER_CONSUMPTION_DAY_TWO_TWICE = USER_CONSUMPTION_DAY_TWO +\
    USER_CONSUMPTION_DAY_TWO

RETURN_VALUES_DAY_ONE = ('2020-02-24 00:00:00.000000', '52d7c87f8c26433dbd095048ad30c8cf',
                         0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)

RETURN_VALUES_DAY_TWO = ('2020-02-25 00:00:00.000000', '52d7c87f8c26433dbd095048ad30c8cf',
                         21.749714, 21.749714, 2, 10.874857, 10.874857, 1, 10.874857, 3969)

BASE_VALUES = {'date': datetime(2020, 2, 25).date(), 'consumption': 0.0,
               'consumption_cumulated': 0.0, 'inhabitants': 2, 'pkv': 0.0,
               'pkv_cumulated': 0.0, 'days': 0, 'moving_average': 0.0,
               'moving_average_annualized': 0}

PKV_DAY_ONE = {'date': datetime(2020, 2, 25).date(), 'consumption': 21.749714,
               'consumption_cumulated': 21.749714, 'inhabitants': 2,
               'pkv':  10.874857, 'pkv_cumulated': 10.874857,
               'days': 1, 'moving_average': 10.874857, 'moving_average_annualized': 3969}

PKV_DAY_TWO = {'date': datetime(2020, 2, 26).date(), 'consumption': 15.0,
               'consumption_cumulated': 36.749714, 'inhabitants': 2,
               'pkv': 7.5, 'pkv_cumulated': 18.374857, 'days': 2,
               'moving_average': 9.1874285, 'moving_average_annualized': 3353}


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

        day_zero = datetime(2020, 2, 24).date()
        day_one = datetime(2020, 2, 25).date()
        self.base_values = PKV(
            day_zero, self.test_user.meter_id, 0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)
        self.pkv_day_one = PKV(day_one, self.test_user.meter_id, 21.749714, 21.749714, 2,
                               10.874857, 10.874857, 1, 10.874857, 3969)
        db.session.add(self.base_values)
        db.session.add(self.pkv_day_one)

        db.session.commit()

        self.client.post(
            '/login', data=json.dumps({'user': 'test@test.net', 'password': 'some_password'}))

    def test_check_input_parameter_date(self):
        """ Unit tests for function check_input_parameter_date().
        Expect False if the date to check lies in the future, True otherwise. """

        good_date = datetime(2020, 1, 2).date()
        bad_date = datetime.today().date() + timedelta(days=1)
        result_good_date = check_input_parameter_date(good_date)
        result_bad_date = check_input_parameter_date(bad_date)

        # Check result types
        self.assertIsInstance(result_good_date, bool)
        self.assertIsInstance(result_bad_date, bool)

        # Check result values
        self.assertEqual(result_good_date, True)
        self.assertEqual(result_bad_date, False)

    @skip
    def test_get_data_day_before(self):
        """ Unit tests for function get_data_day_before(). """

        start = datetime(2020, 2, 25).date()
        day_zero = datetime(2020, 2, 24).date()
        data_day_before = get_data_day_before(start, self.test_user.meter_id)
        data_day_zero = get_data_day_before(day_zero,
                                            self.test_user.meter_id)

        # Check return types
        self.assertIsInstance(data_day_before, RowProxy)
        self.assertIsInstance(data_day_zero, type(None))
        self.assertIsInstance(data_day_before[0], str)
        self.assertIsInstance(data_day_before[1], str)
        self.assertIsInstance(data_day_before[2], float)
        self.assertIsInstance(data_day_before[3], float)
        self.assertIsInstance(data_day_before[4], int)
        self.assertIsInstance(data_day_before[5], float)
        self.assertIsInstance(data_day_before[6], float)
        self.assertIsInstance(data_day_before[7], int)
        self.assertIsInstance(data_day_before[8], float)
        self.assertIsInstance(data_day_before[9], int)

        # Check return sizes
        self.assertEqual(len(data_day_before), 10)

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
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_TWICE)
    @mock.patch('sqlalchemy.engine.result.ResultProxy.first',
                return_value=RETURN_VALUES_DAY_ONE)
    def test_calc_pkv(self, _get_meter_reading_date, _get, first):
        """ Unit tests for function calc_pkv(). """

        start = datetime(2020, 2, 25).date()
        result_day_one = calc_pkv(
            self.test_user.meter_id, self.test_user.inhabitants, start)

        # Check result type
        self.assertIsInstance(result_day_one, (dict, type(None)))

        # Check result values
        if isinstance(result_day_one, dict):
            for param in 'date', 'consumption', 'consumption_cumulated',\
                         'inhabitants', 'pkv', 'pkv_cumulated', 'days',\
                         'moving_average', 'moving_average_annualized':
                self.assertEqual(result_day_one.get(
                    param), PKV_DAY_ONE.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_TWO)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_TWO_TWICE)
    @mock.patch('sqlalchemy.engine.result.ResultProxy.first', return_value=RETURN_VALUES_DAY_TWO)
    def test_calc_pkv_day_two(self, _get_meter_reading_date, _get, first):
        """ Unit tests for function calc_pkv() on day 2. """
        day_two = datetime(2020, 2, 26).date()
        result_day_two = calc_pkv(self.test_user.meter_id,
                                  self.test_user.inhabitants, day_two)

        # Check result type
        self.assertIsInstance(result_day_two, (dict, type(None)))

        # Check result values
        if isinstance(result_day_two, dict):
            for param in 'date', 'consumption', 'consumption_cumulated',\
                         'inhabitants', 'pkv', 'pkv_cumulated', 'days',\
                         'moving_average', 'moving_average_annualized':
                self.assertEqual(result_day_two.get(
                    param), PKV_DAY_TWO.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE)
    def test_get_first_meter_reading_date(self, scan_iter, get):
        """ Unit tests for function get_first_meter_reading_date() """

        start = datetime(2020, 2, 25).date()
        result = get_first_meter_reading_date(self.test_user.meter_id, start)

        # Check result types
        self.assertIsInstance(result, (int, type(None)))