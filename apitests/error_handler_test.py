from flask import Flask
from flask_testing import TestCase
from flask_api import status


class ErrorHandlerTest(TestCase):
    """Checks whether an unknown route results in an HTTP 404 not found."""

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0

        return app

    def test_unknown_route(self):
        response = self.client.get("/non_existing_route/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
