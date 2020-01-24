import json
from datetime import datetime, timedelta
from discovergy.discovergy import Discovergy
import redis
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.task import get_all_meter_ids, calc_end,\
    calc_one_year_back, calc_support_year_start, calc_support_week_start,\
    calc_one_week_back, calc_two_days_back, client_name, Task


ALL_METER_IDS = ['dca0ec32454e4bdd9ed719fbc9fb75d6', '6fdbd41a93d8421cac4ea033203844d1',
                 'bf60438327b1498c9df4e43fc9327849', '0a0f65e992c042e4b86956f3f080114d']


class TaskTestCase(BuzznTestCase):
    """ Unit tests for class Task and helper methods. """

    def setUp(self):
        """ Create test users and a test group in the database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                         'TestToken', 'dca0ec32454e4bdd9ed719fbc9fb75d6', 1)
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.add(User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                            'TestToken2', '6fdbd41a93d8421cac4ea033203844d1',
                            1))
        db.session.add(User(GenderType.MALE, 'danny', 'stey', 'danny@buzzn.net',
                            'TestToken3', 'bf60438327b1498c9df4e43fc9327849', 1))
        db.session.add(Group('TestGroup',
                             '0a0f65e992c042e4b86956f3f080114d'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))
        self.task = Task()

    def test_get_all_meter_ids(self):
        """ Unit tests for function get_all_meter_ids(). """

        result = get_all_meter_ids(db.session)

        # Check return types
        self.assertTrue(isinstance(result, list))
        for meter_id in result:
            self.assertTrue(isinstance(meter_id, str))
            self.assertTrue(meter_id.isalnum())

        # Check return values
        self.assertEqual(result, ALL_METER_IDS)
        for meter_id in result:
            self.assertEqual(len(meter_id), 32)

    def test_calc_end(self):
        """ Unit tests for function calc_end(). """

        result = calc_end()

        # Check return type
        self.assertTrue(isinstance(result, int))

    def test_calc_one_year_back(self):
        """ Unit tests for function calc_one_year_back(). """

        result = calc_one_year_back()

        # Check return type
        self.assertTrue(isinstance(result, int))

    def test_calc_support_year_start(self):
        """ Unit tests for function calc_support_year_start().
        Expect Mar-12 last year if today is between Jan-01 and
        Mar-11.
        Expect Mar-12 this year if today is after Mar-11.
        """

        result = calc_support_year_start()

        # Check result type
        self.assertTrue(isinstance(result, int))

        # Check result values
        date = datetime.fromtimestamp(
            float(result/1000))
        self.assertEqual(date.day, 12)
        self.assertEqual(date.month, 3)
        if (datetime.utcnow().month < date.month) or (datetime.utcnow().day <
                                                      date.day):
            self.assertEqual(date.year, datetime.utcnow().year - 1)
        else:
            self.assertEqual(date.year, datetime.utcnow().year)

    def test_calc_support_week_start(self):
        """ Unit tests for function calc_support_week_start().
        Expect one week back if today is before Mar-12 or after Mar-18.
        Expect start of support year, i.e. Mar-12 this year, if today is
        between Mar-11 and Mar-19.
        """

        result = calc_support_week_start()

        # Check result type
        self.assertTrue(isinstance(result, int))

        # Check result values
        date = datetime.fromtimestamp(
            float(result/1000))
        if (datetime.utcnow().month == 3) and (11 < datetime.utcnow().day < 19):
            self.assertEqual(date.year, datetime.utcnow().year)
            self.assertEqual(date.month, 3)
            self.assertEqual(date.day, 12)
        else:
            self.assertEqual(date.date(), (datetime.utcnow() -
                                           timedelta(days=7)).date())

    def test_calc_one_week_back(self):
        """ Unit tests for function calc_one_week_back(). """

        result = calc_one_week_back()

        # Check return type
        self.assertTrue(isinstance(result, int))

    def test_calc_two_days_back(self):
        """ Unit tests for function calc_two_days_back(). """

        result = calc_two_days_back()

        # Check return type
        self.assertTrue(isinstance(result, int))

    def check_init(self):
        """ Unit tests for function Task.__init__(). """

        # Check class variables
        self.assertTrue(isinstance(self.task.d, Discovergy))
        self.assertTrue(isinstance(self.task.redis_client, redis.Redis))
        self.assertEqual(self.task.d.client_name, client_name)
