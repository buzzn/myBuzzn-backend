from unittest import mock
import discovergy
from tests.buzzn_test_case import BuzznTestCase


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    @mock.patch('discovergy.discovergy.Discovergy.login', return_value=True)
    def test_route_exists(self, login):
        """ Check whether route '/individual-consumption-history' exists. """

        response = self.client.get('/individual-consumption-history')
        self.assertEqual(response.status_code, 206)