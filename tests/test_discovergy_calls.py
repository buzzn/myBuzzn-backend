from unittest import mock
from flask_api import status
from tests.buzzn_test_case import BuzznTestCase


READINGS = [{'time': 1574244000000, 'values': {'power': 0, 'power3': -27279,
                                               'energyOut': 0, 'power1': 0,
                                               'energy': 2180256872214000,
                                               'power2': -2437}},
            {'time': 1574247600000, 'values': {'power': 0, 'power3': -25192,
                                               'energyOut': 0, 'power1': 0,
                                               'energy': 2180256872214000,
                                               'power2': -2443}}]


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    # pylint does not get the required argument from the @mock.patch decorator
    # pylint: disable=unused-argument
    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    @mock.patch('discovergy.discovergy.Discovergy.get_readings',
                return_value=READINGS)
    def test_route_exists(self, login, get_readings):
        """ Check whether route '/individual-consumption-history' exists. """

        response = self.client.get('/individual-consumption-history')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
