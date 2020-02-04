from datetime import datetime
import json
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.energy_saving_calculation import get_all_user_meter_ids,\
    calc_ratio_values, get_meter_reading_date,\
    calc_energy_consumption_last_term, calc_energy_consumption_ongoing_term,\
    calc_estimated_energy_consumption


ALL_USER_METER_IDS = ['b4234cd4bed143a6b9bd09e347e17d34',
                      '52d7c87f8c26433dbd095048ad30c8cf', '117154df05874f41bfdaebcae6abfe98']


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
        # self.start = datetime(2020, 1, 1).date()
        self.start = datetime(2020, 2, 3).date()

    def test_get_all_user_meter_ids(self):
        """ Unit tests for function get_all_user_meter_ids(). """

        result = get_all_user_meter_ids(db.session)

        # Check return types
        self.assertTrue(isinstance(result, list))
        for meter_id in result:
            self.assertTrue(isinstance(meter_id, str))
            self.assertTrue(meter_id.isalnum())

        # Check return values
        self.assertEqual(result, ALL_USER_METER_IDS)
        for meter_id in result:
            self.assertEqual(len(meter_id), 32)

    def test_calc_ratio_values(self):
        """ Unit tests for function calc_ratio_values(). """

        result = calc_ratio_values(self.start)

        # Check result type
        self.assertTrue(isinstance(result, float))

        # Check result value
        self.assertTrue(100.00 >= result >= 0.0)

    def test_get_meter_reading_date(self):
        """ Unit tests for function get_meter_reading_date() """

        for meter_id in ALL_USER_METER_IDS:
            result = get_meter_reading_date(meter_id, self.start)

            # Check result types
            self.assertTrue(isinstance(result, (int, type(None))))

    def test_calc_energy_consumption_last_term(self):
        """ Unit tests for function calc_energy_consumption_last_term() """

        for meter_id in ALL_USER_METER_IDS:
            result = calc_energy_consumption_last_term(meter_id, self.start)

            # Check result types
            self.assertTrue(isinstance(result, (int, type(None))))

    def test_calc_energy_consumption_ongoing_term(self):
        """ Unit tests for function calc_energy_consumption_ongoing_term() """

        for meter_id in ALL_USER_METER_IDS:
            result = calc_energy_consumption_ongoing_term(meter_id,
                                                          self.start)

            # Check result types
            self.assertTrue(isinstance(result, (int, type(None))))

    def test_calc_estimated_energy_consumption(self):
        """ Unit tests for function calc_estimated_energy_consumption() """

        for meter_id in ALL_USER_METER_IDS:
            result = calc_estimated_energy_consumption(meter_id, self.start)

            # Check result types
            self.assertTrue(isinstance(result, (float, type(None))))
