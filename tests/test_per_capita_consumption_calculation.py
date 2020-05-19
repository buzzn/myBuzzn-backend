from datetime import datetime, timedelta
import json
from unittest import mock
from models.per_capita_consumption import PerCapitaConsumption
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import BASE_VALUES, DAY_ONE, SORTED_KEYS_DAY_ONE, DAY_TWO, DAY_ZERO,\
    PCC_DAY_ONE, PCC_DAY_TWO, SORTED_KEYS_DAY_TWO, USER_CONSUMPTION_DAY_ONE,\
    USER_CONSUMPTION_DAY_ONE_TWICE, USER_CONSUMPTION_DAY_TWO_TWICE
from util.database import db
from util.per_capita_consumption_calculation import define_base_values, \
    calc_per_capita_consumption, get_first_meter_reading_date, check_input_parameter_date,\
    get_data_day_before, build_data_package


class PerCapitaConsumptionCalculationTestCase(BuzznTestCase):
    """ Unit tests for per capita consumption calculation methods. """

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

        self.base_values = PerCapitaConsumption(
            DAY_ZERO, self.test_user.meter_id, 0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)
        self.pcc_day_one = PerCapitaConsumption(DAY_ONE, self.test_user.meter_id, 2.1749714,
                                                2.1749714, 2, 1.0874857, 1.0874857, 1,
                                                1.0874857, 397)
        db.session.add(self.base_values)
        db.session.add(self.pcc_day_one)

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
        self.assertIsInstance(data_day_one.per_capita_consumption, float)
        self.assertIsInstance(
            data_day_one.per_capita_consumption_cumulated, float)
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
                         'consumption_cumulated', 'inhabitants', 'per_capita_consumption',\
                         'per_capita_consumption_cumulated', 'days', 'moving_average',\
                         'moving_average_annualized':
                self.assertEqual(result.get(param),
                                 BASE_VALUES.__dict__.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_TWICE)
    def test_calc_per_capita_consumption(self, _scan_iter, _get):
        """ Unit tests for function calc_per_capita_consumption(). """

        start = DAY_ONE
        result_day_one = calc_per_capita_consumption(
            self.test_user.meter_id, self.test_user.inhabitants, start, db.session)

        # Check result type
        self.assertIsInstance(result_day_one, (dict, type(None)))

        # Check result values
        if isinstance(result_day_one, dict):
            for param in 'date.year', 'date.month', 'date.day', 'consumption',\
                         'consumption_cumulated', 'inhabitants', 'per_capita_consumption',\
                         'per_capita_consumption_cumulated', 'days', 'moving_average', \
                         'moving_average_annualized':
                self.assertEqual(result_day_one.get(
                    param), PCC_DAY_ONE.__dict__.get(param))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_TWO)
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_TWO_TWICE)
    def test_calc_per_capita_consumption_day_two(self, _scan_iter, _get):
        """ Unit tests for function calc_per_capita_consumption() on day 2. """
        result_day_two = calc_per_capita_consumption(self.test_user.meter_id,
                                                     self.test_user.inhabitants, DAY_TWO,
                                                     db.session)

        # Check result type
        self.assertIsInstance(result_day_two, (dict, type(None)))

        # Check result values
        if isinstance(result_day_two, dict):
            for param in 'date.year', 'date.month', 'date.day', 'consumption',\
                         'consumption_cumulated', 'inhabitants', 'per_capita_consumption',\
                         'per_capita_consumption_cumulated', 'days', 'moving_average', \
                         'moving_average_annualized':
                self.assertEqual(result_day_two.get(
                    param), PCC_DAY_TWO.__dict__.get(param))

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
                                                  PCC_DAY_ONE.consumption,
                                                  PCC_DAY_ONE.inhabitants,
                                                  PCC_DAY_ONE.date)

        # Check return types
        self.assertIsInstance(data_package_day_one, dict)
        self.assertIsInstance(data_package_day_one.get('date'), datetime)
        self.assertIsInstance(data_package_day_one.get('consumption'), float)
        self.assertIsInstance(data_package_day_one.get(
            'consumption_cumulated'), float)
        self.assertIsInstance(data_package_day_one.get('inhabitants'), int)
        self.assertIsInstance(data_package_day_one.get(
            'per_capita_consumption'), float)
        self.assertIsInstance(data_package_day_one.get(
            'per_capita_consumption_cumulated'), float)
        self.assertIsInstance(data_package_day_one.get('days'), int)
        self.assertIsInstance(
            data_package_day_one.get('moving_average'), float)
        self.assertIsInstance(data_package_day_one.get(
            'moving_average_annualized'), int)

        # Check return values
        self.assertEqual(data_package_day_one['consumption_cumulated'],
                         BASE_VALUES.consumption_cumulated +
                         PCC_DAY_ONE.consumption)
        self.assertEqual(data_package_day_one['per_capita_consumption'],
                         PCC_DAY_ONE.consumption / PCC_DAY_ONE.inhabitants)
        self.assertEqual(data_package_day_one['per_capita_consumption_cumulated'],
                         BASE_VALUES.per_capita_consumption_cumulated +
                         data_package_day_one['per_capita_consumption'])
        self.assertEqual(data_package_day_one['days'], BASE_VALUES.days + 1)
        self.assertEqual(data_package_day_one['moving_average'],
                         data_package_day_one['per_capita_consumption_cumulated'] /
                         data_package_day_one['days'])
        self.assertEqual(data_package_day_one['moving_average_annualized'],
                         round(data_package_day_one['moving_average'] * 365))
