from datetime import datetime, timedelta
import json
from unittest import mock
from models.pkv import PKV
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.pkv_calculation import define_base_values, calc_pkv,\
    get_first_meter_reading_date, check_input_parameter_date,\
    get_data_day_before, build_data_package

DAY_ONE = datetime.today() - timedelta(days=1)
KEY1_DAY_ONE = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_ONE.strftime('%Y-%m-%d') + ' 12:02:00'
KEY2_DAY_ONE = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_ONE.strftime('%Y-%m-%d') + ' 12:07:00'
KEY3_DAY_ONE = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_ONE.strftime('%Y-%m-%d') + ' 12:40:00'
SORTED_KEYS_DAY_ONE = [bytes(KEY1_DAY_ONE, 'utf-8'), bytes(
    KEY2_DAY_ONE, 'utf-8'), bytes(KEY3_DAY_ONE, 'utf-8')]

DAY_TWO = datetime.today()
KEY1_DAY_TWO = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_TWO.strftime('%Y-%m-%d') + ' 12:02:00'
KEY2_DAY_TWO = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_TWO.strftime('%Y-%m-%d') + ' 12:07:00'
KEY3_DAY_TWO = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_TWO.strftime('%Y-%m-%d') + ' 12:40:00'
SORTED_KEYS_DAY_TWO = [bytes(KEY1_DAY_TWO, 'utf-8'), bytes(
    KEY2_DAY_TWO, 'utf-8'), bytes(KEY3_DAY_TWO, 'utf-8')]

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

DAY_ZERO = datetime.today() - timedelta(days=2)
TEST_USER_METER_ID = '52d7c87f8c26433dbd095048ad30c8cf'
BASE_VALUES = PKV(DAY_ZERO, TEST_USER_METER_ID,
                  0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)
PKV_DAY_ONE = PKV(DAY_ONE, TEST_USER_METER_ID, 2174.9714, 2174.9714, 2,
                  1087.4857, 1087.4857, 1, 1087.4857, 396932)
PKV_DAY_TWO = PKV(DAY_TWO, TEST_USER_METER_ID, 1500.0, 3674.9714, 2, 750.0,
                  1837.4857, 2, 918.74285, 335341)


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

        self.base_values = PKV(
            DAY_ZERO, self.test_user.meter_id, 0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)
        self.pkv_day_one = PKV(DAY_ONE, self.test_user.meter_id, 2174.9714, 2174.9714, 2,
                               1087.4857, 1087.4857, 1, 1087.4857, 396932)
        db.session.add(self.base_values)
        db.session.add(self.pkv_day_one)

        db.session.commit()

        self.client.post(
            '/login', data=json.dumps({'user': 'test@test.net', 'password': 'some_password'}))

    def test_check_input_parameter_date(self):
        """ Unit tests for function check_input_parameter_date().
        Expect False if the date to check lies in the future, True otherwise. """

        good_date = datetime(2020, 1, 2, 0, 0, 0)
        bad_date = datetime.today() + timedelta(days=1)
        result_good_date = check_input_parameter_date(good_date)
        result_bad_date = check_input_parameter_date(bad_date)

        # Check result types
        self.assertIsInstance(result_good_date, bool)
        self.assertIsInstance(result_bad_date, bool)

        # Check result values
        self.assertEqual(result_good_date, True)
        self.assertEqual(result_bad_date, False)

    def test_get_data_day_before(self):
        """ Unit tests for function get_data_day_before(). """

        data_day_zero = get_data_day_before(
            DAY_ZERO, self.test_user.meter_id, db.session)
        data_day_one = get_data_day_before(
            DAY_ONE, self.test_user.meter_id, db.session)

        # Check return types
        self.assertIsInstance(data_day_zero, type(None))
        self.assertIsInstance(data_day_one.date, datetime)
        self.assertIsInstance(data_day_one.consumption, float)
        self.assertIsInstance(data_day_one.consumption_cumulated, float)
        self.assertIsInstance(data_day_one.inhabitants, int)
        self.assertIsInstance(data_day_one.pkv, float)
        self.assertIsInstance(data_day_one.pkv_cumulated, float)
        self.assertIsInstance(data_day_one.days, int)
        self.assertIsInstance(data_day_one.moving_average, float)
        self.assertIsInstance(data_day_one.moving_average_annualized, int)

        # Check return values
        self.assertEqual(data_day_zero, None)
        self.assertEqual(data_day_one, self.base_values)

    def test_define_base_values(self):
        """ Unit tests for function define_base_values(). """

        start = DAY_ONE
        result = define_base_values(self.test_user.inhabitants, start)

        # Check return type
        self.assertIsInstance(result, (dict, type(None)))

        # Check return values
        if isinstance(result, dict):
            for param in 'date.year', 'date.month', 'date.day', 'consumption',\
                         'consumption_cumulated', 'inhabitants', 'pkv',\
                         'pkv_cumulated', 'days', 'moving_average',\
                         'moving_average_annualized':
                self.assertEqual(result.get(param),
                                 BASE_VALUES.__dict__.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_TWICE)
    def test_calc_pkv(self, _scan_iter, _get):
        """ Unit tests for function calc_pkv(). """

        start = DAY_ONE
        result_day_one = calc_pkv(
            self.test_user.meter_id, self.test_user.inhabitants, start, db.session)

        # Check result type
        self.assertIsInstance(result_day_one, (dict, type(None)))

        # Check result values
        if isinstance(result_day_one, dict):
            for param in 'date.year', 'date.month', 'date.day', 'consumption',\
                         'consumption_cumulated', 'inhabitants', 'pkv',\
                         'pkv_cumulated', 'days', 'moving_average', 'moving_average_annualized':
                self.assertEqual(result_day_one.get(
                    param), PKV_DAY_ONE.__dict__.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_TWO)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_TWO_TWICE)
    def test_calc_pkv_day_two(self, _scan_iter, _get):
        """ Unit tests for function calc_pkv() on day 2. """
        result_day_two = calc_pkv(self.test_user.meter_id,
                                  self.test_user.inhabitants, DAY_TWO,
                                  db.session)

        # Check result type
        self.assertIsInstance(result_day_two, (dict, type(None)))

        # Check result values
        if isinstance(result_day_two, dict):
            for param in 'date.year', 'date.month', 'date.day', 'consumption',\
                         'consumption_cumulated', 'inhabitants', 'pkv',\
                         'pkv_cumulated', 'days', 'moving_average', 'moving_average_annualized':
                self.assertEqual(result_day_two.get(
                    param), PKV_DAY_TWO.__dict__.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE)
    def test_get_first_meter_reading_date(self, scan_iter, get):
        """ Unit tests for function get_first_meter_reading_date(). """

        start = DAY_ONE.date()
        result = get_first_meter_reading_date(self.test_user.meter_id, start)

        # Check result types
        self.assertIsInstance(result, (int, type(None)))

    def test_build_data_package(self):
        """ Unit tests for function build_data_package(). """

        data_package_day_one = build_data_package(BASE_VALUES,
                                                  PKV_DAY_ONE.consumption,
                                                  PKV_DAY_ONE.inhabitants,
                                                  PKV_DAY_ONE.date)

        # Check return types
        self.assertIsInstance(data_package_day_one, dict)
        self.assertIsInstance(data_package_day_one.get('date'), datetime)
        self.assertIsInstance(data_package_day_one.get('consumption'), float)
        self.assertIsInstance(data_package_day_one.get(
            'consumption_cumulated'), float)
        self.assertIsInstance(data_package_day_one.get('inhabitants'), int)
        self.assertIsInstance(data_package_day_one.get('pkv'), float)
        self.assertIsInstance(data_package_day_one.get('pkv_cumulated'), float)
        self.assertIsInstance(data_package_day_one.get('days'), int)
        self.assertIsInstance(
            data_package_day_one.get('moving_average'), float)
        self.assertIsInstance(data_package_day_one.get(
            'moving_average_annualized'), int)

        # Check return values
        self.assertEqual(data_package_day_one['consumption_cumulated'],
                         BASE_VALUES.consumption_cumulated +
                         PKV_DAY_ONE.consumption)
        self.assertEqual(data_package_day_one['pkv'],
                         PKV_DAY_ONE.consumption/PKV_DAY_ONE.inhabitants)
        self.assertEqual(data_package_day_one['pkv_cumulated'],
                         BASE_VALUES.pkv_cumulated + data_package_day_one['pkv'])
        self.assertEqual(data_package_day_one['days'], BASE_VALUES.days + 1)
        self.assertEqual(data_package_day_one['moving_average'],
                         data_package_day_one['pkv_cumulated']/data_package_day_one['days'])
        self.assertEqual(data_package_day_one['moving_average_annualized'],
                         round(data_package_day_one['moving_average'] * 365))
