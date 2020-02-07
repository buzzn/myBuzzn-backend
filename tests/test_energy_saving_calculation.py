from unittest import mock, skip
from datetime import datetime, time
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
SORTED_KEYS = [[b"b4234cd4bed143a6b9bd09e347e17d34_2020-02-07 00:00:00",
                b"b4234cd4bed143a6b9bd09e347e17d34_2020-02-07 01:00:00",
                b"b4234cd4bed143a6b9bd09e347e17d34_2020-02-07 02:00:00"],
               [b"52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 00:00:00",
                b"52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 01:00:00",
                b"52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 02:00:00"],
               [b"117154df05874f41bfdaebcae6abfe98_2020-02-07 00:00:00",
                b"117154df05874f41bfdaebcae6abfe98_2020-02-07 01:00:00",
                b"117154df05874f41bfdaebcae6abfe98_2020-02-07 02:00:00"]]
DATA = [b'{"type": "reading", "values": {"energy": 1512027002819000}}',
        b'{"type": "reading", "values": {"energy": 1512028877416000}}',
        b'{"type": "reading", "values": {"energy": 1512032408202000}}',
        b'{"type": "reading", "values": {"energy": 1512027002819000}}',
        b'{"type": "reading", "values": {"energy": 1512028877416000}}',
        b'{"type": "reading", "values": {"energy": 1512032408202000}}',
        b'{"type": "reading", "values": {"energy": 1512027002819000}}',
        b'{"type": "reading", "values": {"energy": 1512028877416000}}',
        b'{"type": "reading", "values": {"energy": 1512032408202000}}']


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
    @mock.patch('redis.Redis.scan_iter', side_effect=SORTED_KEYS)
    @mock.patch('redis.Redis.get', side_effect=DATA)
    def test_get_meter_reading_date(self, scan_iter, get):
        """ Unit tests for function get_meter_reading_date() """

        start = datetime(2020, 2, 7).date()
        for meter_id in ALL_USER_METER_IDS:
            result = get_meter_reading_date(meter_id, start)

            # Check result types
            print(result)
            # self.assertIsInstance(result, (int, type(None)))

    @skip
    def test_calc_energy_consumption_last_term(self):
        """ Unit tests for function calc_energy_consumption_last_term() """

        start = datetime(2019, 3, 12).date()
        for meter_id in ALL_USER_METER_IDS:
            result = calc_energy_consumption_last_term(meter_id, start)

            # Check result types
            self.assertIsInstance(result, (int, type(None)))

    @skip
    def test_calc_energy_consumption_ongoing_term(self):
        """ Unit tests for function calc_energy_consumption_ongoing_term() """

        start = datetime(2019, 3, 12).date()
        for meter_id in ALL_USER_METER_IDS:
            result = calc_energy_consumption_ongoing_term(meter_id, start)

            # Check result types
            self.assertIsInstance(result, (int, type(None)))

    @skip
    def test_calc_estimated_energy_consumption(self):
        """ Unit tests for function calc_estimated_energy_consumption() """

        start = datetime(2019, 3, 12).date()
        for meter_id in ALL_USER_METER_IDS:
            result = calc_estimated_energy_consumption(meter_id, start)

            # Check result types
            self.assertIsInstance(result, (float, type(None)))

    @skip
    def test_calc_estimated_energy_saving(self):
        """ Unit tests for function calc_estimated_energy_saving() """

        start = datetime(2019, 3, 12).date()
        for meter_id in ALL_USER_METER_IDS:
            result = calc_estimated_energy_saving(meter_id, start)

            # Check result types
            self.assertIsInstance(result, (float, type(None)))

    @skip
    def test_estimate_energy_saving_each_users(self):
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
