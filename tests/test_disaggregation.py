import ast
import json
from unittest import mock
from flask_api import status
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import EMPTY_RESPONSE, DISAGGREGATION,\
    INDIVIDUAL_DISAGGREGATION


class IndividualDisaggregation(BuzznTestCase):
    """ Unit tests for IndividualDisaggregation. """

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_default_disaggregation', return_value=DISAGGREGATION)
    def test_individual_disaggregation(self, get_disaggregation):
        """ Unit tests for individual_disaggregation(). """

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
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

    # pylint does not understand the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_default_disaggregation', return_value=EMPTY_RESPONSE)
    def test_group_disaggregation(self, get_default_disaggregation):
        """ Unit tests for group_disaggregation(). """

        # Check if route exists
        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
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

    # pylint: disable=unused-argument
    @mock.patch('routes.disaggregation.get_disaggregation',
                return_value=EMPTY_RESPONSE)
    @mock.patch('routes.disaggregation.get_default_disaggregation',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, get_disaggregation, get_default_disaggregation):
        """ Test handling of erroneous parameters. """

        login_request = self.client.post('/login',
                                         data=json.dumps({'user': 'test@test.net',
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
