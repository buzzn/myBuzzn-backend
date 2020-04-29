from models.user import User, GenderType
from models.group import Group
from util.database import db
from util.sqlite_helpers import get_all_meter_ids, get_all_users, get_all_user_meter_ids
from tests.buzzn_test_case import BuzznTestCase
from tests.string_constants import ALL_METER_IDS, ALL_USER_METER_IDS


class TestSqliteHelpers(BuzznTestCase):
    """ Unit test for SQLite helper functions. """

    def setUp(self):
        """ Create test users and a test group in the database. """

        db.drop_all()
        db.create_all()
        self.test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                              'TestToken', ALL_USER_METER_IDS[0], 1)
        db.session.add(self.test_user)
        self.test_user2 = User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                               'TestToken2', ALL_USER_METER_IDS[1], 1)
        db.session.add(self.test_user2)
        self.test_user3 = User(GenderType.MALE, 'danny', 'stey', 'danny@buzzn.net',
                               'TestToken3', ALL_USER_METER_IDS[2], 1)
        db.session.add(self.test_user3)
        db.session.add(Group('TestGroup',
                             ALL_METER_IDS[3],
                             ALL_METER_IDS[4],
                             ALL_METER_IDS[5]))
        db.session.commit()

    def test_get_all_meter_ids(self):
        """ Unit tests for function get_all_meter_ids(). """

        result = get_all_meter_ids(db.session)

        # Check return types
        self.assertIsInstance(result, list)
        for meter_id in result:
            self.assertIsInstance(meter_id, str)
            self.assertTrue(meter_id.isalnum())

        # Check return values
        self.assertEqual(result, ALL_METER_IDS)

    def test_get_all_users(self):
        """ Unit tests for function get_all_users(). """

        result = get_all_users(db.session)

        # Check result types
        self.assertIsInstance(result, list)
        for user in result:
            self.assertIsInstance(user, User)

        # Check result values
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], self.test_user)
        self.assertEqual(result[1], self.test_user2)
        self.assertEqual(result[2], self.test_user3)

    def test_get_all_user_meter_ids(self):
        """ Unit tests for function get_all_user_meter_ids(). """

        result = get_all_user_meter_ids(db.session)

        # Check return types
        self.assertIsInstance(result, list)
        for meter_id in result:
            self.assertIsInstance(meter_id, str)
            self.assertTrue(meter_id.isalnum())

        # Check return values
        self.assertEqual(result, ALL_USER_METER_IDS)
