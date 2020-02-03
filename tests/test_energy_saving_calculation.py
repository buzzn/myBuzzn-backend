from datetime import datetime
import json
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.energy_saving_calculation import get_all_user_meter_ids, calc_ratio_values


ALL_USER_METER_IDS = ['dca0ec32454e4bdd9ed719fbc9fb75d6',
                      '6fdbd41a93d8421cac4ea033203844d1', 'bf60438327b1498c9df4e43fc9327849']


class EnergySavingCalculationTestCase(BuzznTestCase):
    """ Unit tests for energy saving calculation methods. """

    def setUp(self):
        """ Create test users, test group and load profile in the database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                         'TestToken', 'dca0ec32454e4bdd9ed719fbc9fb75d6', 1)
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.add(User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                            'TestToken2', '6fdbd41a93d8421cac4ea033203844d1',
                            1))
        db.session.add(User(GenderType.MALE, 'danny', 'stey', 'danny@buzzn.net',
                            'TestToken3', 'bf60438327b1498c9df4e43fc9327849', 1))
        db.session.add(Group('TestGroup',
                             '0a0f65e992c042e4b86956f3f080114d'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))

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

        start = datetime(2020, 1, 1).date()
        result = calc_ratio_values(start)

        # Check result type
        self.assertTrue(isinstance(result, float))

        # Check result value
        self.assertTrue(100.00 >= result >= 0.0)
