import ast
import json
from flask_api import status
from models.pkv import PKV
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from routes.per_capita_consumption import get_moving_average_annualized
from tests.test_pkv_calculation import DAY_ZERO, DAY_ONE, PKV_DAY_ONE


class PKVTestCase(BuzznTestCase):
    """ Unit tests for PKV route and functions(). """

    def setUp(self):
        """ Create test user and test PKV values in the database. """

        super().setUp()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', '52d7c87f8c26433dbd095048ad30c8cf', 1)
        self.test_user.inhabitants = 2
        self.test_user.set_password('some_password')
        self.test_user.state = StateType.ACTIVE
        db.session.add(self.test_user)

        self.base_values = PKV(
            DAY_ZERO, self.test_user.meter_id, 0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)
        self.pkv_day_one = PKV(DAY_ONE, self.test_user.meter_id, 2174.9714, 2174.9714, 2,
                               1087.4857, 1087.4857, 1, 1087.4857, 396932)
        db.session.add(self.base_values)
        db.session.add(self.pkv_day_one)
        db.session.commit()

    def test_get_moving_average_annualized(self):
        """ Unit tests for function get_moving_average_annualized(). """

        result = get_moving_average_annualized(self.test_user.meter_id)

        # Check result type
        self.assertIsInstance(result, dict)

        # Check result values
        self.assertEqual(result[DAY_ONE.strftime('%Y-%m-%d %H:%M:%S')],
                         PKV_DAY_ONE.moving_average_annualized)

    def test_per_capita_consumption(self):
        """ Unit tests for function per_capita_consumption(). """

        # Check if route exists
        login_request = self.client.post('/login', data=json.dumps({'user':
                                                                    'test@test.net',
                                                                    'password':
                                                                    'some_password'}))
        response = self.client.get('/per-capita-consumption',
                                   headers={'Authorization': 'Bearer {}'.
                                                             format(login_request.json
                                                                    ["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertIsInstance(response.data, bytes)

        for key, value in ast.literal_eval(response.data.decode('utf-8')).items():
            self.assertEqual(
                key, PKV_DAY_ONE.date.strftime('%Y-%m-%d %H:%M:%S'))
            self.assertEqual(value, PKV_DAY_ONE.moving_average_annualized)