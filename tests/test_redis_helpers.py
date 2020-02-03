import os
import redis
from tests.buzzn_test_case import BuzznTestCase
from util.redis_helpers import get_sorted_keys


ALL_USER_METER_IDS = ['b4234cd4bed143a6b9bd09e347e17d34',
                      '52d7c87f8c26433dbd095048ad30c8cf', '117154df05874f41bfdaebcae6abfe98']


class RedisHelpersTestCase(BuzznTestCase):
    """ Unit tests for redis helper methods. """

    def setUp(self):
        """ Init redis client """

        redis_host = os.environ['REDIS_HOST']
        redis_port = os.environ['REDIS_PORT']
        redis_db = os.environ['REDIS_DB']
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)

    def test_get_sorted_keys(self):
        """ Unit tests for function get_sorted_keys() """

        for meter_id in ALL_USER_METER_IDS:

            # Check result types
            self.assertTrue(isinstance(get_sorted_keys(self.redis_client,
                                                       meter_id), list))
