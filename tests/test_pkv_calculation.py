from datetime import datetime
import json
from unittest import mock
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.pkv_calculation import define_base_values


USER_CONSUMPTION = 3737464542963000
BASE_VALUES = {'date': '2020-02-25', 'consumption': 3737464.542963,
               'consumption_cumulated': 3737464.542963, 'inhabitants': 2,
               'pkv': 1868732.2714815, 'pkv_cumulated': 1868732.2714815,
               'days': 0, 'moving_average': 0, 'moving_average_annualized': 0}


class PKVCalculationTestCase(BuzznTestCase):
    """ Unit tests for PKV calculation methods. """

    def setUp(self):
        """ Create test user and test group in the database. """

        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', 'b4234cd4bed143a6b9bd09e347e17d34', 1)
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password')
        self.test_user.state = StateType.ACTIVE
        db.session.add(self.test_user)
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))

    # pylint: disable=unused-argument
    @mock.patch('util.energy_saving_calculation.get_meter_reading_date',
                return_value=USER_CONSUMPTION)
    def test_define_base_values(self, _get_meter_reading_date):
        """ Unit tests for function define_base_values(). """

        start = datetime(2020, 2, 26).date()
        result = define_base_values(self.test_user.meter_id,
                                    self.test_user.inhabitants, start)

        # Check return type
        self.assertTrue(isinstance(result, dict))

        # Check return values
        for param in 'date', 'consumption', 'consumption_cumulated',\
                     'inhabitants', 'pkv', 'pkv_cumulated', 'days', 'moving_average'\
                     'moving_average_annualized':
            self.assertEqual(result.get(param), BASE_VALUES.get(param))
