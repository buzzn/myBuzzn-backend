import ast
from datetime import datetime
import json
from unittest import mock
from flask_api import status
from models.user import User, GenderType, StateType
from models.savings import UserSaving, CommunitySaving
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.sqlite_helpers import estimate_energy_saving_each_user,\
    estimate_energy_saving_all_users
from routes.global_challenge import get_individual_saving, get_community_saving,\
    get_individual_baseline
from tests.string_constants import COMMUNITY_SAVING, COMMUNITY_SAVING_DICT, INDIVIDUAL_BASELINE,\
    INDIVIDUAL_GLOBAL_CHALLENGE, INDIVIDUAL_SAVING, INDIVIDUAL_SAVING_DICT,\
    READINGS_ESTIMATION, SORTED_KEYS_ESTIMATION


class GlobalChallengeTestCase(BuzznTestCase):
    """ Unit tests for global challenge methods. """

    def setUp(self):
        """ Create test user, test group and load profile in the database. """

        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', '52d7c87f8c26433dbd095048ad30c8cf', 1)
        self.test_user.flat_size = 60.0
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password1')
        self.test_user.state = StateType.ACTIVE
        self.test_user.baseline = 19361634120995
        test_first_timestamp = datetime(2020, 2, 13, 9, 57, 3)
        test_first_user_saving = UserSaving(test_first_timestamp,
                                            '52d7c87f8c26433dbd095048ad30c8cf',
                                            3148577026610.7812)
        test_second_timestamp = datetime(2020, 1, 13, 9, 57, 3)
        test_second_user_saving = UserSaving(test_second_timestamp,
                                             '52d7c87f8c26433dbd095048ad30c8cf',
                                             3259689137721.8923)
        test_first_community_saving = CommunitySaving(
            test_first_timestamp, 85184267259376.5)
        test_second_community_saving = CommunitySaving(
            test_second_timestamp, 86295378361487.6)
        db.session.add(self.test_user)
        db.session.add(test_first_user_saving)
        db.session.add(test_second_user_saving)
        db.session.add(test_first_community_saving)
        db.session.add(test_second_community_saving)
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password1'}))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_ESTIMATION)
    @mock.patch('redis.Redis.get', side_effect=READINGS_ESTIMATION)
    def test_estimate_energy_saving_each_user(self, scan_iter, get):
        """ Unit tests for function estimate_energy_saving_each_user(). """

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
    @mock.patch('redis.Redis.get', side_effect=READINGS_ESTIMATION)
    def test_estimate_energy_saving_all_users(self, scan_iter, get):
        """ Unit tests for function estimate_energy_saving_each_user(). """

        start = datetime(2019, 3, 12).date()
        result = estimate_energy_saving_all_users(start, db.session)

        # Check result type
        self.assertIsInstance(result, float)

    # pylint: disable=unused-argument
    @mock.patch('sqlalchemy.engine.result.ResultProxy.first',
                return_value=INDIVIDUAL_SAVING)
    @mock.patch('sqlalchemy.create_engine')
    def test_get_individual_saving(self, first, create_engine):
        """ Unit tests for function get_individual_saving(). """

        result = get_individual_saving(self.test_user.meter_id)

        # Check result types
        self.assertIsInstance(result, (dict, type(None)))
        if isinstance(result, dict):
            for key, value in result.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, float)

                # Check result values
                self.assertEqual(key, INDIVIDUAL_SAVING[0].split('.')[0])
                self.assertEqual(value, INDIVIDUAL_SAVING[1])

    # pylint: disable=unused-argument
    @mock.patch('sqlalchemy.engine.result.ResultProxy.first', return_value=COMMUNITY_SAVING)
    @mock.patch('sqlalchemy.create_engine')
    def test_get_community_saving(self, first, create_engine):
        """ Unit tests for function get_community_saving(). """

        result = get_community_saving()

        # Check result types
        self.assertIsInstance(result, (dict, type(None)))
        if isinstance(result, dict):
            for key, value in result.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, float)

    # pylint: disable=unused-argument
    @mock.patch('sqlalchemy.engine.result.ResultProxy.first', return_value=INDIVIDUAL_BASELINE)
    @mock.patch('sqlalchemy.create_engine')
    def test_get_individual_baseline(self, create_engine, first):
        """ Unit tests for function get_individual_baseline(). """

        result = get_individual_baseline(self.test_user.id)

        # Check result type
        self.assertIsInstance(result, int)

        # Check result values
        self.assertEqual(result, self.test_user.baseline)

    # pylint: disable=unused-argument
    @mock.patch('routes.global_challenge.get_individual_saving',
                return_value=INDIVIDUAL_SAVING_DICT)
    @mock.patch('routes.global_challenge.get_individual_baseline',
                return_value=INDIVIDUAL_BASELINE)
    def test_individual_global_challenge(self, _get_individual_saving,
                                         _get_individual_baseline):
        """ Unit tests for individual_global_challenge(). """

        # Check if route exists
        login_request = self.client.post('/login', data=json.dumps({'user':
                                                                    'test@test.net',
                                                                    'password':
                                                                    'some_password1'}))
        response = self.client.get('/individual-global-challenge',
                                   headers={'Authorization': 'Bearer {}'.
                                                             format(login_request.
                                                                    json["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertIsInstance(response.data, bytes)

        self.assertEqual(ast.literal_eval(
            response.data.decode('utf-8')), INDIVIDUAL_GLOBAL_CHALLENGE)

    # pylint: disable=unused-argument
    @mock.patch('routes.global_challenge.get_community_saving',
                return_value=COMMUNITY_SAVING_DICT)
    def test_community_global_challenge(self, _get_community_saving):
        """ Unit tests for community_global_challenge(). """

        # Check if route exists
        response = self.client.get('/community-global-challenge')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertIsInstance(response.data, bytes)
        self.assertEqual(ast.literal_eval(response.data.decode('utf-8')),
                         COMMUNITY_SAVING_DICT)
