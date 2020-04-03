import ast
import json
from unittest import mock
from flask_api import status
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db


CONSUMPTION = {"2020-01-15 10:00:04": {'power': 27279, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437},
               "2020-01-15 10:01:10": {'power': 27200, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437}}
EMPTY_RESPONSE = {}
INDIVIDUAL_CONSUMPTION = {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                     '2020-01-15 10:01:10': 2180256872214000},
                          'power': {'2020-01-15 10:00:04': 27279, '2020-01-15 10:01:10': 27200}}
EMPTY_RESPONSE_BYTES = {'energy': {}, 'power': {}}
GROUP_CONSUMPTION = {'consumed_energy': {"2020-01-15 10:00:04": 2180256872214000,
                                         "2020-01-15 10:01:10": 2180256872214000},
                     'consumed_power': {"2020-01-15 10:00:04": 27279,
                                        "2020-01-15 10:01:10": 27200},
                     'produced_first_meter_energy': {"2020-01-15 10:00:04": 2180256872214000,
                                                     "2020-01-15 10:01:10": 2180256872214000},
                     'produced_first_meter_power': {"2020-01-15 10:00:04": 27279,
                                                    "2020-01-15 10:01:10": 27200},
                     'produced_second_meter_energy': {"2020-01-15 10:00:04": 2180256872214000,
                                                      "2020-01-15 10:01:10": 2180256872214000},
                     'produced_second_meter_power': {"2020-01-15 10:00:04": 27279,
                                                     "2020-01-15 10:01:10": 27200}}
EMPTY_GROUP_CONSUMPTION = {'consumed_energy': {}, 'consumed_power': {},
                           'produced_first_meter_energy': {},
                           'produced_first_meter_power': {},
                           'produced_second_meter_energy': {},
                           'produced_second_meter_power': {}}
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
        self.target_user.meter_id = 'EASYMETER_60404854'
        db.session.add(self.target_user)
        db.session.commit()

    # pylint does not understand the required argument from the @mock.patch decorator
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
            'SomeGroup',
            'EASYMETER_60327599',
            '2c52403eef11408dbec88ae5f61e1ee7',
            'EASYMETER_60404854')
        db.session.add(self.target_group)
        db.session.commit()

    # pylint does not understand the required argument from the @mock.patch decorator
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
        self.target_user.meter_id = 'EASYMETER_1124001747'
        db.session.add(self.target_user)
        db.session.commit()

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_default_disaggregation', return_value=DISAGGREGATION)
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
        self.target_user.meter_id = 'EASYMETER_60404854'
        self.target_user.group_id = 1
        db.session.add(self.target_user)
        self.target_group = Group(
            "SomeGroup",
            'EASYMETER_1124001747',
            '5e769d5b83934bccae11a8fa95e0dc5f',
            'e2a7468f0cf64b7ca3f3d1350b893c6d')
        db.session.add(self.target_group)
        db.session.commit()

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_default_disaggregation', return_value=EMPTY_RESPONSE)
    def test_group_disaggregation(self, get_default_disaggregation):
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
        self.target_user.meter_id = 'EASYMETER_60404854'
        self.target_user.group_id = 1
        db.session.add(self.target_user)
        self.target_group = Group(
            'SomeGroup',
            '52d7c87f8c26433dbd095048ad30c8cf',
            'EASYMETER_60404852',
            'EASYMETER_60327599')
        db.session.add(self.target_group)
        db.session.commit()

    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_disaggregation',
                return_value=EMPTY_RESPONSE)
    @mock.patch('routes.disaggregation.get_default_disaggregation',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_disaggregation, get_default_disaggregation):
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
