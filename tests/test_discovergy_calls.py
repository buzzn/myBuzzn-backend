# import json
from flask_api import status
from tests.buzzn_test_case import BuzznTestCase
# from routes.consumption_history import IndividualConsumptionHistory
# from routes.consumption_history import GroupConsumptionHistory
# from routes.disaggregation import IndividualDisaggregation
# from routes.disaggregation import GroupDisaggregation


class IndividualConsumptionHistoryTestCase(BuzznTestCase):
    """ Unit tests for route IndividualConsumptionHistory. """

    def setup(self):
        self.app = self.create_app()

    def test_route_exists(self):
        """ Check whether route '/individual-consumption-history' exists. """

        response = self.client.get('/individual-consumption-history')
        # self.assertEqual(response.status_code, 200)
