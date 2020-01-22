from unittest import mock
from models.user import User, GenderType, StateType
from models.group import Group
from tests.buzzn_test_case import BuzznTestCase
from util.database import db
from util.task import create_session, get_all_meter_ids, calc_end,\
    calc_one_year_back, calc_support_year_start, calc_support_week_start,\
    calc_one_week_back, calc_two_days_back, Task


class TaskTestCase(BuzznTestCase):
    """ Unit tests for class Task and helper methods. """

    def setUp(self):
        """ Create test users and a test group in the database. """

        db.drop_all()
        db.create_all()
        test_user = User(GenderType.MALE, 'Some', 'User', 'test@test.net',
                         'TestToken', 'dca0ec32454e4bdd9ed719fbc9fb75d6')
        test_user.flat_size = 60.0
        test_user.inhabitants = 2
        test_user.set_password('some_password')
        test_user.state = StateType.ACTIVE
        db.session.add(test_user)
        db.session.add(User(GenderType.FEMALE, 'judith', 'greif', 'judith@buzzn.net',
                            'TestToken2', '6fdbd41a93d8421cac4ea033203844d1',
                            1))
        db.session.add(User(GenderType.MALE, 'danny', 'stay', 'danny@buzzn.net',
                            'TestToken3', 'bf60438327b1498c9df4e43fc9327849', 1))
        db.session.add(Group('TestGroup',
                             '0a0f65e992c042e4b86956f3f080114d'))
        db.session.commit()
        self.client.post('/login', data=json.dumps({'user': 'test@test.net',
                                                    'password': 'some_password'}))
