from datetime import datetime
import os
from unittest import mock
import redis
from tests.buzzn_test_case import BuzznTestCase
from models.user import User, GenderType, StateType
from tests.string_constants import FIRST_METER_READING_DATE, DAY_ONE, FIRST_ENERGY_DATE, \
    USER_CONSUMPTION_DAY_ONE_ITERATION_FIRST, USER_CONSUMPTION_DAY_ONE_ITERATION_LAST, \
    SORTED_KEYS_DAY_ONE, LAST_ENERGY_DATE, LAST_METER_READING_DATE, KEY1_DAY_ONE, \
    DATE_KEY1_DAY_ONE, KEY_LAST, EMPTY_RESPONSE_ARRAY
from util.database import db
from util.redis_helpers import get_first_meter_reading_date, get_last_meter_reading_date, \
    get_entry_date


class RedisHelpersTestCase(BuzznTestCase):
    """ Unit tests for redis helpers methods. """

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', '52d7c87f8c26433dbd095048ad30c8cf', 1)
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password1')
        self.test_user.state = StateType.ACTIVE
        db.session.add(self.test_user)
        db.session.commit()
        redis_host = os.environ['REDIS_HOST']
        redis_port = os.environ['REDIS_PORT']
        redis_db = os.environ['REDIS_DB']
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', return_value=FIRST_METER_READING_DATE)
    def test_get_entry_date(self, get):
        """ Unit tests for function get_entry_date(). """
        entry_date, data = get_entry_date(self.redis_client, self.test_user.meter_id, KEY1_DAY_ONE,
                                          'reading')
        # Check data type
        self.assertIsInstance(data, dict)
        # Check entry_date value
        self.assertEqual(entry_date, DATE_KEY1_DAY_ONE)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', return_value=FIRST_METER_READING_DATE)
    def test_get_entry_date_wrong_type(self, get):
        """ Unit tests for function get_entry_date() if entry has wrong type. """
        entry_date, data = get_entry_date(self.redis_client, self.test_user.meter_id, KEY1_DAY_ONE,
                                          'disaggregation')
        # Check entry_date value
        self.assertEqual(entry_date, None)
        self.assertEqual(data, None)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', return_value=FIRST_METER_READING_DATE)
    def test_get_entry_date_wrong_key_format(self, get):
        """ Unit tests for function get_entry_date() if key has wrong format. """
        entry_date, data = get_entry_date(self.redis_client, self.test_user.meter_id, KEY_LAST,
                                          'reading')
        # Check entry_date value
        self.assertEqual(entry_date, None)
        self.assertEqual(data, None)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', return_value=FIRST_METER_READING_DATE)
    def test_get_first_meter_reading_date(self, get):
        """ Unit tests for function get_first_meter_reading_date(). """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_first_meter_reading_date(self.redis_client, self.test_user.meter_id, date)
        # Check result types
        self.assertIsInstance(result, (float, type(None)))
        # Check result values
        self.assertEqual(result, FIRST_ENERGY_DATE)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_ITERATION_FIRST)
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    def test_get_first_meter_reading_date_no_first_key(self, get, scan_iter):
        """ Unit tests for function get_first_meter_reading_date() if iteration is needed. """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_first_meter_reading_date(self.redis_client, self.test_user.meter_id, date)
        # Check result types
        self.assertIsInstance(result, (int, type(None)))
        # Check result values
        self.assertEqual(result, FIRST_ENERGY_DATE)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_ITERATION_FIRST)
    @mock.patch('redis.Redis.scan_iter', return_value=EMPTY_RESPONSE_ARRAY)
    def test_get_first_meter_reading_date_no_keys(self, get, scan_iter):
        """ Unit tests for function get_first_meter_reading_date() if no keys are available. """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_first_meter_reading_date(self.redis_client, self.test_user.meter_id, date)
        # Check result values
        self.assertEqual(result, None)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', return_value=LAST_METER_READING_DATE)
    def test_get_last_meter_reading_date(self, get):
        """ Unit tests for function get_last_meter_reading_date(). """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_last_meter_reading_date(self.redis_client, self.test_user.meter_id, date)
        # Check result types
        self.assertIsInstance(result, (float, type(None)))
        # Check result values
        self.assertEqual(result, LAST_ENERGY_DATE)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_ITERATION_LAST)
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    def test_get_last_meter_reading_date_no_last_key(self, get, scan_iter):
        """ Unit tests for function get_last_meter_reading_date() if iteration is needed. """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_last_meter_reading_date(self.redis_client, self.test_user.meter_id, date)
        # Check result types
        self.assertIsInstance(result, (int, type(None)))
        # Check result values
        self.assertEqual(result, LAST_ENERGY_DATE)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.get', side_effect=USER_CONSUMPTION_DAY_ONE_ITERATION_LAST)
    @mock.patch('redis.Redis.scan_iter', return_value=EMPTY_RESPONSE_ARRAY)
    def test_get_last_meter_reading_date_no_keys(self, get, scan_iter):
        """ Unit tests for function get_last_meter_reading_date() if no keys are available. """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_last_meter_reading_date(self.redis_client, self.test_user.meter_id, date)
        # Check result values
        self.assertEqual(result, None)
