from datetime import datetime
import json
from unittest import mock
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.energy_saving_calculation import estimate_energy_saving_each_user,\
    estimate_energy_saving_all_users
from tests.test_energy_saving_calculation import SORTED_KEYS_ESTIMATION,\
    DATA_ESTIMATION


class GlobalChallengeTestCase(BuzznTestCase):
    """ Unit tests for global challenge methods. """

    def setUp(self):
        """ Create test user, test group and load profile in the database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                         'TestToken', '52d7c87f8c26433dbd095048ad30c8cf', 1)
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_ESTIMATION)
    @mock.patch('redis.Redis.get', side_effect=DATA_ESTIMATION)
    def test_estimate_energy_saving_each_user(self, scan_iter, get):
        """ Unit tests for function estimate_energy_saving_each_user() """

        start = datetime(2019, 3, 12).date()
        result = estimate_energy_saving_each_user(start, db.session)

        # Check result types
        self.assertIsInstance(result, dict)
        for key, value in result.items():
            self.assertTrue(key.isalnum())
            self.assertIsInstance(value, (float, type(None)))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_ESTIMATION)
    @mock.patch('redis.Redis.get', side_effect=DATA_ESTIMATION)
    def test_estimate_energy_saving_all_users(self, scan_iter, get):
        """ Unit tests for function estimate_energy_saving_each_user() """

        start = datetime(2019, 3, 12).date()
        result = estimate_energy_saving_all_users(start, db.session)

        # Check result type
        self.assertIsInstance(result, float)