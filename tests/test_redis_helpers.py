from datetime import datetime
import os
import redis
from unittest import mock
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import FIRST_METER_READING_DATE, DAY_ONE, FIRST_ENERGY_DATE, \
    USER_CONSUMPTION_DAY_ONE, SORTED_KEYS_DAY_ONE
from util.redis_helpers import get_first_meter_reading_date


class RedisHelpersTestCase(BuzznTestCase):
    """ Unit tests for redis helpers methods. """

    def setUp(self):
        super().setUp()
        redis_host = os.environ['REDIS_HOST']
        redis_port = os.environ['REDIS_PORT']
        redis_db = os.environ['REDIS_DB']
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    @mock.patch('redis.Redis.get', return_value=FIRST_METER_READING_DATE)
    def test_get_first_meter_reading_date(self, get):
        """ Unit tests for function get_first_meter_reading_date(). """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_first_meter_reading_date(self.redis_client, self.test_case_user.meter_id,
                                              date)
        # Check result types
        self.assertIsInstance(result, (float, type(None)))
        self.assertEqual(result, FIRST_ENERGY_DATE)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS_DAY_ONE)
    @mock.patch('redis.Redis.get', side_effects=USER_CONSUMPTION_DAY_ONE)
    def test_get_first_meter_reading_date_no_first_key(self, scan_iter, get):
        """ Unit tests for function get_first_meter_reading_date(). """
        date = datetime.strftime(DAY_ONE.date(), '%Y-%m-%d')
        result = get_first_meter_reading_date(self.redis_client, self.test_case_user.meter_id, date)

        # Check result types
        self.assertIsInstance(result, (int, type(None)))