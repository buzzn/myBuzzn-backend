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

# byte objects cannot be line-split
# pylint: disable=line-too-long
GROUP_CONSUMPTION = b'{"consumed":{"1574982000000":0,"1574985600000":0},"produced":{"1574982000000":0,"1574985600000":0}}\n'
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

        # Check erroneous input
        response_wrong_timestamp_format = self.client.get(
            '/individual-consumption-history?begin=123.123')
        response_wrong_parameter = self.client.get(
            '/individual-consumption-history?tocs=five_minutes')

        # Check response content
        self.assertEqual(
            response_wrong_timestamp_format.status_code, status.HTTP_200_OK)
        self.assertEqual(response_wrong_parameter.status_code,
                         status.HTTP_200_OK)

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=EMPTY_RESPONSE, side_effect=ValueError)
    def test_erroneous_tics_format(self, login, get_readings):
        """ Check handling of erroneous tics format. """

        response = self.client.get(
            '/individual-consumption-history?tics=five_minutes')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)

        # Check response content
        self.assertEqual(response.data, b'{}\n')


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

        # Check erroneous input
        response_wrong_timestamp_format = self.client.get(
            '/group-consumption-history?begin=123.123')
        response_wrong_parameter = self.client.get(
            '/group-consumption-history?and=1575284400000')

        # Check response content
        self.assertEqual(
            response_wrong_timestamp_format.status_code, status.HTTP_200_OK)
        self.assertEqual(response_wrong_parameter.status_code,
                         status.HTTP_200_OK)


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
