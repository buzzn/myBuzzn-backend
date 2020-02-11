from unittest import mock, skip
from datetime import datetime
import json
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.energy_saving_calculation import get_all_user_meter_ids,\
    calc_ratio_values, get_meter_reading_date,\
    calc_energy_consumption_last_term, calc_energy_consumption_ongoing_term,\
    calc_estimated_energy_consumption, calc_estimated_energy_saving,\
    estimate_energy_saving_each_user, estimate_energy_saving_all_users


ALL_USER_METER_IDS = ['b4234cd4bed143a6b9bd09e347e17d34',
                      '52d7c87f8c26433dbd095048ad30c8cf', '117154df05874f41bfdaebcae6abfe98']

RETURN_VALUES = [(1002846.2290000044,), (896919.8780000011,)]

SORTED_KEYS = [b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 00:00:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 01:00:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 02:00:00']

DATA = [b'{"type": "reading", "values": {"energy": 1512027002819000}}',
        b'{"type": "reading", "values": {"energy": 1512028877416000}}',
        b'{"type": "reading", "values": {"energy": 1512032408202000}}']

SORTED_KEYS_LAST_TERM = [
    [b'52d7c87f8c26433dbd095048ad30c8cf_2020-03-11 04:15:00'],
    [b'52d7c87f8c26433dbd095048ad30c8cf_2019-03-12 04:15:00']]

LAST_READING_ONGOING_TERM = bytes(
    '52d7c87f8c26433dbd095048ad30c8cf_' + datetime.today().
    strftime('%Y-%m-%d %H:%M:%S'), encoding='utf-8')

SORTED_KEYS_ONGOING_TERM = [
    [LAST_READING_ONGOING_TERM],
    [b'52d7c87f8c26433dbd095048ad30c8cf_2019-03-12 04:15:00']]

DATA_LAST_TERM = [
    b'{"type": "reading", "values": {"energy": 1512027005000000}}',
    b'{"type": "reading", "values": {"energy": 1512027002819000}}']

DATA_ONGOING_TERM = [
    b'{"type": "reading", "values": {"energy": 1512027009000000}}',
    b'{"type": "reading", "values": {"energy": 1512027005000100}}']

SORTED_KEYS_ALL_TERMS = [[b'52d7c87f8c26433dbd095048ad30c8cf_2019-03-11 01:00:00'],
                         [b'52d7c87f8c26433dbd095048ad30c8cf_2018-03-12 01:00:00'],
                         SORTED_KEYS_ONGOING_TERM[0], SORTED_KEYS_ONGOING_TERM[1]]

DATA_ALL_TERMS = [DATA_LAST_TERM[0], DATA_LAST_TERM[1], DATA_ONGOING_TERM[0],
                  DATA_ONGOING_TERM[1]]

SORTED_KEYS_ESTIMATION = [SORTED_KEYS_ALL_TERMS[0],
                          SORTED_KEYS_ALL_TERMS[1]] + SORTED_KEYS_ALL_TERMS

DATA_ESTIMATION = [DATA_ALL_TERMS[0], DATA_ALL_TERMS[1]] + DATA_ALL_TERMS


class EnergySavingCalculationTestCase(BuzznTestCase):
    """ Unit tests for energy saving calculation methods. """

    def setUp(self):
        """ Create test users, test group and load profile in the database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                         'TestToken', 'b4234cd4bed143a6b9bd09e347e17d34', 1)
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.add(User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                            'TestToken2', '52d7c87f8c26433dbd095048ad30c8cf', 1))
        db.session.add(User(GenderType.MALE, 'danny', 'stey', 'danny@buzzn.net',
                            'TestToken3', '117154df05874f41bfdaebcae6abfe98', 1))
        db.session.add(Group('TestGroup',
                             '0a0f65e992c042e4b86956f3f080114d'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))

    def test_get_all_user_meter_ids(self):
        """ Unit tests for function get_all_user_meter_ids(). """

        result = get_all_user_meter_ids(db.session)

        # Check return types
        self.assertIsInstance(result, list)
        for meter_id in result:
            self.assertIsInstance(meter_id, str)
            self.assertTrue(meter_id.isalnum())

        # Check return values
        self.assertEqual(result, ALL_USER_METER_IDS)
        for meter_id in result:
            self.assertEqual(len(meter_id), 32)

    # pylint: disable=unused-argument
    @mock.patch('sqlalchemy.engine.result.ResultProxy.first', side_effect=RETURN_VALUES)
    def test_calc_ratio_values(self, first):
        """ Unit tests for function calc_ratio_values(). """

        start = datetime(2019, 3, 12).date()
        result = calc_ratio_values(start)

        # Check result type
        self.assertIsInstance(result, float)

        # Check result value
        self.assertTrue(1.0 >= result >= 0.0)

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter', return_value=SORTED_KEYS)
    @mock.patch('redis.Redis.get', side_effect=DATA)
    def test_get_meter_reading_date(self, scan_iter, get):
        """ Unit tests for function get_meter_reading_date() """

        start = datetime(2020, 2, 7).date()
        result = get_meter_reading_date(ALL_USER_METER_IDS[1], start)

        # Check result types
        self.assertIsInstance(result, (int, type(None)))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_LAST_TERM)
    @mock.patch('redis.Redis.get', side_effect=DATA_LAST_TERM)
    def test_calc_energy_consumption_last_term(self, scan_iter, get):
        """ Unit tests for function calc_energy_consumption_last_term() """

        start = datetime(2020, 3, 12).date()
        result = calc_energy_consumption_last_term(
            ALL_USER_METER_IDS[1], start)

        # Check result type
        self.assertIsInstance(result, (int, type(None)))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_ONGOING_TERM)
    @mock.patch('redis.Redis.get', side_effect=DATA_ONGOING_TERM)
    def test_calc_energy_consumption_ongoing_term(self, scan_iter, get):
        """ Unit tests for function calc_energy_consumption_ongoing_term() """

        start = datetime(2019, 3, 12).date()
        result = calc_energy_consumption_ongoing_term(ALL_USER_METER_IDS[1],
                                                      start)

        # Check result type
        self.assertIsInstance(result, (int, type(None)))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_ALL_TERMS)
    @mock.patch('redis.Redis.get', side_effect=DATA_ALL_TERMS)
    def test_calc_estimated_energy_consumption(self, scan_iter, get):
        """ Unit tests for function calc_estimated_energy_consumption() """

        start = datetime(2019, 3, 12).date()
        result = calc_estimated_energy_consumption(
            ALL_USER_METER_IDS[1], start)

        # Check result types
        self.assertIsInstance(result, (float, type(None)))

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.scan_iter',
                side_effect=SORTED_KEYS_ESTIMATION)
    @mock.patch('redis.Redis.get', side_effect=DATA_ESTIMATION)
    def test_calc_estimated_energy_saving(self, scan_iter, get):
        """ Unit tests for function calc_estimated_energy_saving() """

        start = datetime(2019, 3, 12).date()
        result = calc_estimated_energy_saving(ALL_USER_METER_IDS[1], start)

        # Check result types
        self.assertIsInstance(result, (float, type(None)))

    @skip
    def test_estimate_energy_saving_each_user(self):
        """ Unit tests for function estimate_energy_saving_each_user() """

        start = datetime(2019, 3, 12).date()
        result = estimate_energy_saving_each_user(start)

        # Check result types
        self.assertIsInstance(result, dict)
        for key, value in result.items():
            self.assertTrue(key.isalnum())
            self.assertIsInstance(value, (float, type(None)))

    @skip
    def test_estimate_energy_saving_all_users(self):
        """ Unit tests for function estimate_energy_saving_each_user() """

        start = datetime(2019, 3, 12).date()
        result = estimate_energy_saving_all_users(start)

        # Check result type
        self.assertIsInstance(result, float)
