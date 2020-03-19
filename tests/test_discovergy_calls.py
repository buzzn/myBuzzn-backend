import ast
import json
from unittest import mock
from flask_api import status
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db


CONSUMPTION = {"2020-01-15 10:00:04": {'power': 0, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437},
               "2020-01-15 10:01:10": {'power': 0, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437}}
EMPTY_RESPONSE = {}
INDIVIDUAL_CONSUMPTION = {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                     '2020-01-15 10:01:10': 2180256872214000},
                          'power': {'2020-01-15 10:00:04': 0, '2020-01-15 10:01:10': 0}}
EMPTY_RESPONSE_BYTES = {'energy': {}, 'power': {}}
GROUP_CONSUMPTION = {'consumed': {"2020-01-15 10:00:04": 0,
                                  "2020-01-15 10:01:10": 0},
                     'produced': {"2020-01-15 10:00:04": 0,
                                  "2020-01-15 10:01:10": 0}}
EMPTY_GROUP_CONSUMPTION = {'consumed': {}, 'produced': {}}
DISAGGREGATION = {"2020-01-15 10:01:04": {"Durchlauferhitzer-1": 0,
                                          "Grundlast-1": 50000000},
                  "2020-01-15 10:01:10": {"Durchlauferhitzer-1": 0,
                                          "Grundlast-1": 50000000}}
INDIVIDUAL_DISAGGREGATION = {"2020-01-15 10:01:04": {'Durchlauferhitzer-1': 0,
                                                     'Grundlast-1': 50000000},
                             "2020-01-15 10:01:10": {'Durchlauferhitzer-1': 0,
                                                     'Grundlast-1': 50000000}}


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    def setUp(self):
        super().setUp()
        self.target_user = User(GenderType.MALE, "Some", "User", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        self.target_user.meter_id = '52d7c87f8c26433dbd095048ad30c8cf'  # 8 words hex value
        db.session.add(self.target_user)
        db.session.commit()

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_readings', return_value=CONSUMPTION)
    def test_individual_consumption_history(self, get_readings):
        """ Unit tests for individual_consumption_history(). """

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
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
    @mock.patch('routes.consumption_history.get_readings', return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_readings):
        """ Check handling of erroneous parameters. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
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
        self.target_user = User(GenderType.MALE, "Some", "User", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        self.target_user.meter_id = 'b2d1ed119bb527b74adc767db48b69d9'  # 8 words hex value
        self.target_user.group_id = 1
        db.session.add(self.target_user)
        self.target_group = Group(
            "SomeGroup", 'b4234cd4bed143a6b9bd09e347e17d34')
        db.session.add(self.target_group)
        db.session.commit()

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_readings', return_value=CONSUMPTION)
    def test_group_consumption_history(self, get_readings):
        """ Unit tests for group_consumption_history()."""

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
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
    @mock.patch('routes.consumption_history.get_readings',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_readings):
        """ Test handling of erroneous parameters. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
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


class IndividualDisaggregation(BuzznTestCase):
    """ Unit tests for IndividualDisaggregation. """

    def setUp(self):
        super().setUp()
        self.target_user = User(GenderType.MALE, "Some", "User", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        self.target_user.meter_id = '269e682dbfd74a569ff4561b6416c999'  # 8 words hex value
        db.session.add(self.target_user)
        db.session.commit()

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_disaggregation', return_value=DISAGGREGATION)
    def test_individual_disaggregation(self, get_disaggregation):
        """ Unit tests for individual_disaggregation(). """

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
                                                          'password': 'some_password'}))
        response = self.client.get('/individual-disaggregation', headers={
            'Authorization': 'Bearer {}'.format(login_request.json["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(ast.literal_eval(
            response.data.decode('utf-8')), INDIVIDUAL_DISAGGREGATION)


class GroupDisaggregation(BuzznTestCase):
    """ Unit tests for GroupDisaggregation. """

    def setUp(self):
        super().setUp()
        self.target_user = User(GenderType.MALE, "Some", "User", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        self.target_user.meter_id = 'b2d1ed119bb527b74adc767db48b69d9'  # 8 words hex value
        self.target_user.group_id = 1
        db.session.add(self.target_user)
        self.target_group = Group(
            "SomeGroup", '52d7c87f8c26433dbd095048ad30c8cf')
        db.session.add(self.target_group)
        db.session.commit()

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_disaggregation',
                return_value=EMPTY_RESPONSE)
    def test_group_disaggregation(self, get_disaggregation):
        """ Unit tests for group_disaggregation(). """

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
                                                          'password': 'some_password'}))
        response = self.client.get('/group-disaggregation', headers={
            'Authorization': 'Bearer {}'.format(login_request.json["sessionToken"])})

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(ast.literal_eval(
            response.data.decode('utf-8')), EMPTY_RESPONSE)


class Disaggregation(BuzznTestCase):
    """ Unit test for common funcionalities of IndividualDisaggregation and
    GroupDisaggregation. """

    def setUp(self):
        super().setUp()
        self.target_user = User(GenderType.MALE, "Some", "User", "user@some.net",
                                "SomeToken", "SomeMeterId", "SomeGroup")
        self.target_user.set_password("some_password")
        self.target_user.state = StateType.ACTIVE
        self.target_user.meter_id = 'b2d1ed119bb527b74adc767db48b69d9'  # 8 words hex value
        self.target_user.group_id = 1
        db.session.add(self.target_user)
        self.target_group = Group(
            "SomeGroup", 'b4234cd4bed143a6b9bd09e347e17d34')
        db.session.add(self.target_group)
        db.session.commit()

    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_disaggregation',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_disaggregation):
        """ Test handling of erroneous parameters. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'User@Some.net',
                                                          'password': 'some_password'}))

        for route in '/individual-disaggregation', '/group-disaggregation':
            response_timestamp_format = self.client.get(
                route + '?begin=123.123', headers={'Authorization':
                                                   'Bearer {}'.
                                                   format(login_request.json["sessionToken"])})

            response_parameter = self.client.get(route + '?and=1575284400000', headers={
                'Authorization': 'Bearer {}'.format(login_request.json["sessionToken"])})

            # Check response status
            self.assertEqual(
                response_timestamp_format.status_code, status.HTTP_200_OK)
            self.assertEqual(response_parameter.status_code,
                             status.HTTP_200_OK)

            # Check response content
            self.assertEqual(ast.literal_eval(
                response_timestamp_format.data.decode('utf-8')), EMPTY_RESPONSE)
            self.assertEqual(ast.literal_eval(
                response_parameter.data.decode('utf-8')), EMPTY_RESPONSE)
