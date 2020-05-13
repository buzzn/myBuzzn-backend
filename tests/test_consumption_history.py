import ast
import json
from unittest import mock
from flask_api import status
from models.user import User, GenderType, StateType
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import CONSUMPTION, EMPTY_GROUP_CONSUMPTION,\
    EMPTY_RESPONSE, EMPTY_RESPONSE_BYTES, GROUP_CONSUMPTION, INDIVIDUAL_CONSUMPTION, \
    FIRST_LAST_ENERGY, AVERAGE_POWER
from util.database import db


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_default_readings', return_value=CONSUMPTION)
    def test_individual_consumption_history(self, get_default_readings):
        """ Unit tests for individual_consumption_history(). """

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
                                                          'password': 'some_password'}))
        response = self.client.get('/individual-consumption-history',
                                   headers={'Authorization': 'Bearer {}'.
                                                             format(login_request.json
                                                                    ["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(ast.literal_eval(
            response.data.decode('utf-8')), INDIVIDUAL_CONSUMPTION)

    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_default_readings', return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_default_readings):
        """ Check handling of erroneous parameters. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
                                                          'password': 'some_password'}))
        response_timestamp_format = self.client.get('/individual-consumption-history?begin=123.123',
                                                    headers={'Authorization':
                                                             'Bearer {}'.
                                                             format(login_request.json
                                                                    ["sessionToken"])})

        response_parameter = self.client.get('/individual-consumption-history?and=1575284400000',
                                             headers={'Authorization':
                                                      'Bearer {}'.
                                                      format(login_request.json
                                                             ["sessionToken"])})
        response_tics_format = self.client.get('individual-consumption-history?tics=five_minutes',
                                               headers={'Authorization':
                                                        'Bearer {}'.
                                                        format(login_request.json
                                                               ["sessionToken"])})

        # Check response status
        self.assertEqual(response_timestamp_format.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response_parameter.status_code, status.HTTP_200_OK)
        self.assertEqual(response_tics_format.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertEqual(ast.literal_eval(
            response_timestamp_format.data.decode('utf-8')), EMPTY_RESPONSE_BYTES)
        self.assertEqual(ast.literal_eval(
            response_parameter.data.decode('utf-8')), EMPTY_RESPONSE_BYTES)
        self.assertEqual(ast.literal_eval(
            response_tics_format.data.decode('utf-8')), EMPTY_RESPONSE_BYTES)


class GroupConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route GroupConsumptionHistory. """

    def setUp(self):
        super().setUp()
        group_member2 = User(GenderType.FEMALE, 'judith', 'greif',
                             'judith@buzzn.net', 'TestToken2',
                             'EASYMETER_60404852', 1)
        group_member2.set_password('some_password2')
        group_member2.state = StateType.ACTIVE
        db.session.add(group_member2)
        db.session.commit()

    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_average_power_for_meter_id_and_date',
                return_value=AVERAGE_POWER)
    @mock.patch('routes.consumption_history.get_first_and_last_energy_for_date',
                return_value=FIRST_LAST_ENERGY)
    def test_group_consumption_history(self, get_average_power_for_meter_id_and_date,
                                       get_first_and_last_energy_for_date):
        """ Unit tests for group_consumption_history()."""

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
                                                          'password': 'some_password'}))
        response = self.client.get('/group-consumption-history', headers={
            'Authorization': 'Bearer {}'.format(login_request.json["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(ast.literal_eval(
            response.data.decode('utf-8')), GROUP_CONSUMPTION)

    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_average_power_for_meter_id_and_date',
                return_value=EMPTY_RESPONSE)
    @mock.patch('routes.consumption_history.get_first_and_last_energy_for_date',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_average_power_for_meter_id_and_date,
                        get_first_and_last_energy_for_date):
        """ Test handling of erroneous parameters. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
                                                          'password': 'some_password'}))
        response_timestamp_format = self.client.get('/group-consumption-history?begin=123.123',
                                                    headers={'Authorization':
                                                             'Bearer {}'.
                                                             format(login_request.json
                                                                    ["sessionToken"])})

        response_parameter = self.client.get('/group-consumption-history?and=1575284400000',
                                             headers={'Authorization':
                                                      'Bearer {}'.
                                                      format(login_request.json
                                                             ["sessionToken"])})
        response_tics_format = self.client.get('group-consumption-history?tics=five_minutes',
                                               headers={'Authorization':
                                                        'Bearer {}'.
                                                        format(login_request.json
                                                               ["sessionToken"])})

        # Check response status
        self.assertEqual(response_timestamp_format.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response_parameter.status_code, status.HTTP_200_OK)
        self.assertEqual(response_tics_format.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertEqual(ast.literal_eval(
            response_timestamp_format.data.decode('utf-8')), EMPTY_GROUP_CONSUMPTION)
        self.assertEqual(ast.literal_eval(
            response_parameter.data.decode('utf-8')), EMPTY_GROUP_CONSUMPTION)
        self.assertEqual(ast.literal_eval(
            response_tics_format.data.decode('utf-8')), EMPTY_GROUP_CONSUMPTION)
