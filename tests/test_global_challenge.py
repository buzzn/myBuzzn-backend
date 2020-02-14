import ast
from datetime import datetime
import json
from unittest import mock
from flask_api import status
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.energy_saving_calculation import estimate_energy_saving_each_user,\
    estimate_energy_saving_all_users
from routes.global_challenge import get_individual_saving, get_community_saving
from tests.test_energy_saving_calculation import SORTED_KEYS_ESTIMATION,\
    DATA_ESTIMATION


INDIVIDUAL_SAVING = ('2020-02-13 09:57:03.620809', 3148577026610.7812)
INDIVIDUAL_SAVING_DICT = {'2020-02-13 09:57:03': 3148577026610.7812}
COMMUNITY_SAVING = ('2020-02-13 16:20:21.977425', 85184267259376.5)
COMMUNITY_SAVING_DICT = {'2020-02-13 16:20:21': 85184267259376.5}
METER_ID = '52d7c87f8c26433dbd095048ad30c8cf'


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
    @mock.patch('redis.Redis.get', side_effect=DATA_ESTIMATION)
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

        result = get_individual_saving(METER_ID)

        # Check result types
        self.assertIsInstance(result, (dict, type(None)))
        if isinstance(result, dict):
            for key, value in result.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, float)

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
    @mock.patch('routes.global_challenge.get_individual_saving',
                return_value=INDIVIDUAL_SAVING_DICT)
    def test_individual_global_challenge(self, _get_individual_saving):
        """ Unit tests for individual_global_challenge(). """

        # Check if route exists
        login_request = self.client.post('/login', data=json.dumps({'user':
                                                                    'test@test.net',
                                                                    'password':
                                                                    'some_password'}))
        response = self.client.get('/individual-global-challenge',
                                   headers={'Authorization': 'Bearer {}'.
                                                             format(login_request.json
                                                                    ["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertIsInstance(response.data, bytes)
        self.assertEqual(ast.literal_eval(response.data.decode('utf-8')),
                         INDIVIDUAL_SAVING_DICT)

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
