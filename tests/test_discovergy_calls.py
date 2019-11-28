from unittest import mock
from tests.buzzn_test_case import BuzznTestCase


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    def test_route_exists(self):
        """ Check whether route '/individual-consumption-history' exists. """

        response = self.client.get('/individual-consumption-history')
        self.assertEqual(response.status_code, 200)
