from unittest import mock
from flask_api import status
from tests.buzzn_test_case import BuzznTestCase


CONSUMPTION = [{'time': 1574982000000, 'values': {'power': 0, 'power3': -27279,
                                                  'energyOut': 0, 'power1': 0,
                                                  'energy': 2180256872214000,
                                                  'power2': -2437}},
               {'time': 1574985600000, 'values': {'power': 0, 'power3': -27279,
                                                  'energyOut': 0, 'power1': 0,
                                                  'energy': 2180256872214000,
                                                  'power2': -2437}}]
EMPTY_RESPONSE = {}
INDIVIDUAL_CONSUMPTION = b'{"1574982000000":0,"1574985600000":0}\n'
EMPTY_RESPONSE_BYTES = b'{}\n'

# byte objects cannot be line-split
# pylint: disable=line-too-long
GROUP_CONSUMPTION = b'{"consumed":{"1574982000000":0,"1574985600000":0},"produced":{"1574982000000":0,"1574985600000":0}}\n'
EMPTY_GROUP_CONSUMPTION = b'{"consumed":{},"produced":{}}\n'
DISAGGREGATION = {
    "1575111600000": {
        "Durchlauferhitzer-1": 0,
        "Grundlast-1": 50000000
    },
    "1575112500000": {
        "Durchlauferhitzer-1": 0,
        "Grundlast-1": 50000000
    }
}

# byte objects cannot be line-split
# pylint: disable=line-too-long
INDIVIDUAL_DISAGGREGATION = b'{"1575111600000":{"Durchlauferhitzer-1":0,"Grundlast-1":50000000},"1575112500000":{"Durchlauferhitzer-1":0,"Grundlast-1":50000000}}\n'


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=CONSUMPTION)
    def test_individual_consumption_history(self, login, get_readings):
        """ Unit tests for individual_consumption_history(). """

        # Check if route exists
        response = self.client.get('/individual-consumption-history')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(response.data, INDIVIDUAL_CONSUMPTION)

    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, login, get_readings):
        """ Check handling of erroneous parameters. """

        response_timestamp_format = self.client.get(
            '/individual-consumption-history?begin=123.123')
        response_parameter = self.client.get(
            '/individual-consumption-history?and=1575284400000')
        response_tics_format = self.client.get(
            'individual-consumption-history?tics=five_minutes')

        # Check response status
        self.assertEqual(response_timestamp_format.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response_parameter.status_code, status.HTTP_200_OK)
        self.assertEqual(response_tics_format.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertEqual(response_timestamp_format.data,
                         EMPTY_RESPONSE_BYTES)
        self.assertEqual(response_parameter.data, EMPTY_RESPONSE_BYTES)
        self.assertEqual(response_tics_format.data, EMPTY_RESPONSE_BYTES)


class GroupConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route GroupConsumptionHistory. """

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=CONSUMPTION)
    def test_group_consumption_history(self, login, get_readings):
        """ Unit tests for group_consumption_history()."""

        # Check if route exists
        response = self.client.get('/group-consumption-history')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(response.data, GROUP_CONSUMPTION)

    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, login, get_readings):
        """ Test handling of erroneous parameters. """

        response_timestamp_format = self.client.get(
            '/group-consumption-history?begin=123.123')
        response_parameter = self.client.get(
            '/group-consumption-history?and=1575284400000')
        response_tics_format = self.client.get(
            'group-consumption-history?tics=five_minutes')

        # Check response status
        self.assertEqual(response_timestamp_format.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(response_parameter.status_code, status.HTTP_200_OK)
        self.assertEqual(response_tics_format.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertEqual(response_timestamp_format.data,
                         EMPTY_GROUP_CONSUMPTION)
        self.assertEqual(response_parameter.data, EMPTY_GROUP_CONSUMPTION)
        self.assertEqual(response_tics_format.data, EMPTY_GROUP_CONSUMPTION)


class IndividualDisaggregation(BuzznTestCase):
    """ Unit tests for IndividualDisaggregation. """

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_disaggregation',
                return_value=DISAGGREGATION)
    def test_individual_disaggregation(self, login, disaggregation):
        """ Unit tests for individual_disaggregation(). """

        # Check if route exists
        response = self.client.get('/individual-disaggregation')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(response.data, INDIVIDUAL_DISAGGREGATION)


class GroupDisaggregation(BuzznTestCase):
    """ Unit tests for GroupDisaggregation. """

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_disaggregation',
                return_value=EMPTY_RESPONSE)
    def test_group_disaggregation(self, login, disaggregation):
        """ Unit tests for group_disaggregation(). """

        # Check if route exists
        response = self.client.get('/group-disaggregation')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response content
        self.assertTrue(isinstance(response.data, bytes))
        self.assertEqual(response.data, EMPTY_RESPONSE_BYTES)


class Disaggregation(BuzznTestCase):
    """ Unit test for common funcionalities of IndividualDisaggregation and
    GroupDisaggregation. """

    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_disaggregation',
                return_value=EMPTY_RESPONSE)
    def test_parameters(self, login, disaggregation):
        """ Test handling of erroneous parameters. """

        for route in '/individual-disaggregation', '/group-disaggregation':
            response_timestamp_format = self.client.get(
                route + '?begin=123.123')
            response_parameter = self.client.get(route + '?and=1575284400000')

            # Check response status
            self.assertEqual(
                response_timestamp_format.status_code, status.HTTP_200_OK)
            self.assertEqual(response_parameter.status_code,
                             status.HTTP_200_OK)

            # Check response content
            self.assertEqual(response_timestamp_format.data,
                             EMPTY_RESPONSE_BYTES)
            self.assertEqual(response_parameter.data, EMPTY_RESPONSE_BYTES)
