import json
from discovergy.discovergy import Discovergy
import redis
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import READING, READING_NEGATIVE_POWER
from util.database import db
from util.task import check_and_nullify_power_value, client_name, Task


class TaskTestCase(BuzznTestCase):
    """ Unit tests for class Task and helper methods. """

    def setUp(self):
        """ Create test users and a test group in the database. """

        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', 'dca0ec32454e4bdd9ed719fbc9fb75d6', 1)
        self.test_user.flat_size = 60.0
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password1')
        self.test_user.state = StateType.ACTIVE
        db.session.add(self.test_user)
        self.test_user2 = User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                               'TestToken2', '6fdbd41a93d8421cac4ea033203844d1', 1)
        db.session.add(self.test_user2)
        self.test_user3 = User(GenderType.MALE, 'danny', 'stey', 'danny@buzzn.net',
                               'TestToken3', 'bf60438327b1498c9df4e43fc9327849', 1)
        db.session.add(self.test_user3)
        db.session.add(Group('TestGroup',
                             '0a0f65e992c042e4b86956f3f080114d',
                             '5e769d5b83934bccae11a8fa95e0dc5f',
                             'e2a7468f0cf64b7ca3f3d1350b893c6d'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password1'}))
        self.task = Task()

    def test_check_and_nullify_power_value(self):
        """ Unit tests for function check_and_nullify_power_value(). """

        result = check_and_nullify_power_value(
            READING, self.test_user.meter_id)
        result_adjusted = check_and_nullify_power_value(READING_NEGATIVE_POWER,
                                                        self.test_user.meter_id)

        # Check result types
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result_adjusted, dict)

        # Check result values
        self.assertEqual(result['values']['power'], READING['values']['power'])
        self.assertEqual(result_adjusted['values']['power'], 0)

    def check_init(self):
        """ Unit tests for function Task.__init__(). """

        # Check class variables
        self.assertIsInstance(self.task.d, Discovergy)
        self.assertIsInstance(self.task.redis_client, redis.Redis)
        self.assertEqual(self.task.d.client_name, client_name)
