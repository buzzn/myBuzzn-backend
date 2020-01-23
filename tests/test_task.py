import json
from unittest import mock
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

ALL_READINGS = [[{'time': 1552345200000,
                  'values': {'power': 911592,
                             'power3': 306882,
                             'energyOut': 0,
                             'power1': 299087,
                             'energy': 138355326787000,
                             'power2': 301311}},
                 {'time': 1552950000000,
                  'values': {'power': 1225383,
                             'power3': 412563,
                             'energyOut': 0,
                             'power1': 403432,
                             'energy': 140413970813000,
                             'power2': 405330}}],
                [{'time': 1553554800000,
                  'values': {'power': 1908607,
                             'power3': 641592,
                             'energyOut': 0,
                             'power1': 630312,
                             'energy': 143620431118000,
                             'power2': 632905}},
                 {'time': 1554156000000,
                  'values': {'power': 2079448,
                             'power3': 699554,
                             'energyOut': 0,
                             'power1': 687385,
                             'energy': 147093110032000,
                             'power2': 688819}}],
                [{'time': 1554760800000,
                  'values': {'power': 1777410,
                             'power3': 606004,
                             'energyOut': 0,
                             'power1': 594829,
                             'energy': 150079158307000,
                             'power2': 596599}},
                 {'time': 1555365600000,
                  'values': {'power': 1297513,
                             'power3': 436995,
                             'energyOut': 0,
                             'power1': 427617,
                             'energy': 152258980165000,
                             'power2': 429200}}],
                [{'time': 1554760800000,
                  'values': {'power': 1777410,
                             'power3': 606004,
                             'energyOut': 0,
                             'power1': 594829,
                             'energy': 150079158307000,
                             'power2': 596599}},
                 {'time': 1555365600000,
                  'values': {'power': 1297513,
                             'power3': 436995,
                             'energyOut': 0,
                             'power1': 427617,
                             'energy': 152258980165000,
                             'power2': 429200}}]]

ALL_DISAGGREGATION_VALUES = [{'1579189500000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 79999999,
                                                'Backofen-2': 0},
                              '1579190400000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 80000000,
                                                'Backofen-2': 0}},
                             {'1579191300000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 80000000,
                                                'Backofen-2': 0},
                              '1579192200000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 80000000,
                                                'Backofen-2': 0}},
                             {'1579193100000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 79999999,
                                                'Backofen-2': 0},
                              '1579194000000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 80000000,
                                                'Backofen-2': 0}},
                             {'1579193100000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 79999999,
                                                'Backofen-2': 0},
                              '1579194000000': {'Kühlschrank-1': 0,
                                                'Spülmaschine-1': 0,
                                                'Waschmaschine-1': 0,
                                                'Backofen-1': 0,
                                                'Durchlauferhitzer-2': 0,
                                                'Durchlauferhitzer-3': 0,
                                                'Durchlauferhitzer-1': 0,
                                                'Grundlast-1': 80000000,
                                                'Backofen-2': 0}}]


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
        """ Unit tests for function calc_support_year_start(). """

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
        """ Unit tests for function calc_support_week_start(). """

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

    # pylint: disable=unused-argument
    @mock.patch('redis.Redis.flushdb')
    @mock.patch('util.task.create_session')
    @mock.patch('util.task.get_all_meter_ids', return_value=ALL_METER_IDS)
    @mock.patch('util.login')
    @mock.patch('discovergy.discovergy.Discovergy.get_readings', side_effect=ALL_READINGS)
    @mock.patch('redis.Redis.set')
    @mock.patch('discovergy.discovergy.Discovergy.get_disaggregation',
                side_effect=ALL_DISAGGREGATION_VALUES)
    # pylint: disable=too-many-arguments
    def test_populate_redis(self, flush_db, create_session, _get_all_meter_ids,
                            login, get_readings, _set, get_disaggregation):
        """ Unit tests for function populate_redis(). """

        self.task.populate_redis()
