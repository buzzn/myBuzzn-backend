import json
from datetime import datetime

from flask_api import status

from tests.buzzn_test_case import BuzznTestCase
from models.user import User, StateType, GenderType
from routes.reset_password import Errors
from util.database import db


class SetPasswordTest(BuzznTestCase):
    """Checks if users can perform password resets."""

    def test_unknown_user(self):
        """Expect an unknown username requesting a new
        password to result in a bad request."""

        db.session.add(User(GenderType.MALE, "Some", "User", "User@Some.net",
                            "SomeToken", "SomeMeterId", "SomeGroup"))
        db.session.commit()

        response = self.client.post('/password/request-reset-token',
                                    data=json.dumps({'user': 'OtherUser@Some.net'}))

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json, Errors.UNKNOWN_USER.__dict__)

    def test_disabled_user(self):
        """Expect a password reset request from a user with a disabled user
        account resulting in a bad request."""

        target_user = User(GenderType.MALE, "Some", "User", "User@Some.net",
                           "SomeToken", "SomeMeterId", "SomeGroup")
        target_user.set_state(StateType.DEACTIVATED)
        db.session.add(target_user)
        db.session.commit()

        response = self.client.post('/password/request-reset-token',
                                    data=json.dumps({'user': 'User@Some.net'}))

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.json, Errors.DEACTIVATED_USER.__dict__)

    def test_request_password_proper_user(self):
        """Expect on a new password request from a active user account
        resulting in a new token, with a new expiry date and the
        `state password_reset_pending`"""

        db.session.add(User(GenderType.MALE, "Some", "User", "User@Some.net",
                            "SomeToken", "SomeMeterId", "SomeGroup"))
        db.session.commit()

        response = self.client.post('/password/request-reset-token',
                                    data=json.dumps({'user': 'User@Some.net'}))

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)

        target_user = User.query.filter_by(name="User").first()
        self.assertTrue(
            target_user.password_reset_token_expires > datetime.now())
        self.assertEqual(target_user.state,
                         StateType.PASSWORT_RESET_PENDING)
        self.assertIsNotNone(target_user.password_reset_token)
        self.assert_template_used('password/reset_password_mail.txt')

    def test_unknown_token(self):
        """On a new password request from an active user account with an invalid
        token expect to show a failure."""

        target_user = User(GenderType.MALE, "Some", "User", "User@Some.net",
                           "SomeToken", "SomeMeterId", "SomeGroup")
        target_user.generate_password_request_token()
        db.session.add(target_user)
        db.session.commit()

        self.client.post('/password/reset/unknown-token',
                         data=dict(password="somepassword",
                                   passwordRepeat="somepassword"))

        self.assert_template_used('password/failure.html')
