from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from util.error import UNKNOWN_RESSOURCE


class ErrorHandlerTest(BuzznTestCase):
    """Checks whether an unknown route results in an HTTP 404 not found."""

    def test_unknown_route(self):
        response = self.client.get('/bam')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json['name'], UNKNOWN_RESSOURCE.name)
        self.assertEqual(response.json['description'],
                         UNKNOWN_RESSOURCE.description)
