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

CONSUMPTION_2 = {"2020-01-15 10:00:04": {'power': 27279, 'power3': -27279,
                                         'energyOut': 0, 'power1': 0,
                                         'energy': 2180256872214000,
                                         'power2': -2437},
                 "2020-01-15 10:01:10": {'power': 27200, 'power3': -27279,
                                         'energyOut': 0, 'power1': 0,
                                         'energy': 2180256872214000,
                                         'power2': -2437},
                 "2020-01-15 10:03:10": {'power': 27272, 'power3': -27279,
                                         'energyOut': 0, 'power1': 0,
                                         'energy': 2180256872214000,
                                         'power2': -2437}}

FIRST_LAST_ENERGY = [{'2020-01-15 10:00:04': 2180256872214000,
                     '2020-01-15 10:01:10': 2180256872214000},
                     {'2020-01-15 10:00:04': 2180256872214000,
                     '2020-01-15 10:01:10': 2180256872214000},
                     {'2020-01-15 10:00:04': 2180256872214000,
                     '2020-01-15 10:01:10': 2180256872214000},
                     {'2020-01-15 10:00:04': 2180256872214000,
                     '2020-01-15 10:01:10': 2180256872214000},
                     {'2020-01-15 10:00:04': 2180256872214000,
                     '2020-01-15 10:01:10': 2180256872214000}]

FIRST_LAST_ENERGY_2 = {'2020-01-15 10:00:04': 2180256872214000,
                       '2020-01-15 10:01:10': 2180256872214000}

FIRST_LAST_ENERGY_EMPTY = [{}, {}, {}, {}, {},
                           {}, {}, {}, {}, {},
                           {}, {}, {}, {}, {}]

EMPTY_RESPONSE = {}
INDIVIDUAL_CONSUMPTION = {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                     '2020-01-15 10:01:10': 2180256872214000},
                          'power': {'2020-01-15 10:00:04': 27279, '2020-01-15 10:01:10': 27200}}
EMPTY_RESPONSE_BYTES = {'energy': {}, 'power': {}}
GROUP_CONSUMPTION = {'consumed_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                         '2020-01-15 10:01:10': 2180256872214000},
                     'consumed_power': {'2020-01-15 10:00:04': 27279,
                                        '2020-01-15 10:01:10': 27200},
                     'group_users': {'1': {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:01:10': 2180256872214000},
                                           'power': {'2020-01-15 10:00:04': 27279,
                                                     '2020-01-15 10:01:10': 27200}},
                                     '2': {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:01:10': 2180256872214000},
                                           'power': {'2020-01-15 10:00:04': 27279,
                                                     '2020-01-15 10:01:10': 27200}}},
                     'produced_first_meter_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                     '2020-01-15 10:01:10': 2180256872214000},
                     'produced_first_meter_power': {'2020-01-15 10:00:04': 27279,
                                                    '2020-01-15 10:01:10': 27200},
                     'produced_second_meter_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:01:10': 2180256872214000},
                     'produced_second_meter_power': {'2020-01-15 10:00:04': 27279,
                                                     '2020-01-15 10:01:10': 27200}}
EMPTY_GROUP_CONSUMPTION = {'consumed_energy': {},
                           'consumed_power': {},
                           'group_users': {'1': {'energy': {}, 'power': {}},
                                           '2': {'energy': {}, 'power': {}}},
                           'produced_first_meter_energy': {},
                           'produced_first_meter_power': {},
                           'produced_second_meter_energy': {},
                           'produced_second_meter_power': {}}


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
    @mock.patch('routes.consumption_history.get_default_readings', return_value=CONSUMPTION)
    def test_individual_consumption_history(self, get_default_readings):
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
    @mock.patch('routes.consumption_history.get_default_readings', return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_default_readings):
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
        self.target_user.meter_id = 'EASYMETER_60404854'
        self.target_user.group_id = 1
        db.session.add(self.target_user)
        self.target_group = Group(
            'SomeGroup',
            'EASYMETER_60327599',
            '2c52403eef11408dbec88ae5f61e1ee7',
            'EASYMETER_60404854')
        db.session.add(self.target_group)
        group_member2 = User(GenderType.FEMALE, 'judith', 'greif',
                             'judith@buzzn.net', 'TestToken2',
                             'EASYMETER_60404852', 1)
        group_member2.set_password('some_password2')
        group_member2.state = StateType.ACTIVE
        db.session.add(group_member2)
        db.session.commit()

    # pylint: disable=unused-argument
    @mock.patch('routes.consumption_history.get_default_readings', return_value=CONSUMPTION)
    @mock.patch('routes.consumption_history.get_first_and_last_energy_for_date',
                side_effect=FIRST_LAST_ENERGY)
    def test_group_consumption_history(self, get_default_readings,
                                       get_first_and_last_energy_for_date):
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
    @mock.patch('routes.consumption_history.get_default_readings',
                return_value=EMPTY_RESPONSE)
    @mock.patch('routes.consumption_history.get_first_and_last_energy_for_date',
                side_effect=FIRST_LAST_ENERGY_EMPTY)
    def test_parameters(self, get_default_readings, get_first_and_last_energy_for_date):
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
