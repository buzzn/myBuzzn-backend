from datetime import datetime
import json
import logging
import os
import redis
from models.group import Group
from models.user import User
from util.database import db
from util.error import exception_message


logger = logging.getLogger(__name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']


def get_group_meter_id(user_id):
    """ Get the group meter id from the SQLite database for the given user.
    :param int user_id: the user's id
    :return: the group meter id of the group the user belongs to
    :rtype: int
    """

    user = db.session.query(User).filter_by(id=user_id).first()
    group = db.session.query(Group).filter_by(id=user.group_id).first()

    return group.group_meter_id


def get_group_members(user_id):
    """ Get the parameters from the database to create a group data packet for
    the given user.
    :param int user_id: the user's id
    :return: the group members' ids, inhabitants and flat sizes
    :rtype: [dict]
    """

    user = db.session.query(User).filter_by(id=user_id).first()
    group_users = db.session.query(User).filter_by(
        group_id=user.group_id).all()
    group_members = []
    for group_user in group_users:
        group_members.append(dict(id=group_user.id, meter_id=group_user.meter_id,
                                  inhabitants=group_user.inhabitants,
                                  flat_size=group_user.flat_size))

    return group_members


class WebsocketProvider:
    """ Provides a SocketIO object with live data for the clients. """

    def __init__(self):
        """ Create and setup a websocket provider. """

        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)  # connect to server

    def get_sorted_keys(self, meter_id):
        """ Return all keys stored in the redis db for a given meter id.
        :param str meter_id: the meter id to prefix the scan with
        """

        return sorted([key.decode('utf-8') for key in
                       self.redis_client.scan_iter(meter_id + '*')])

    def get_last_reading(self, meter_id):
        """ Return the first meter reading stored in the redis db.
        :param str meter_id: the meter id for which to get the values
        """

        result = dict()
        for key in reversed(self.get_sorted_keys(meter_id)):
            data = self.redis_client.get(key)
            if json.loads(data).get('type') == 'reading':
                result = json.loads(data)
                break
        return result

    def get_first_reading(self, meter_id):
        """ Return the first meter reading stored in the redis db.
        :param str meter_id: the meter id for which to get the values
        """

        result = dict()
        for key in self.get_sorted_keys(meter_id):
            data = self.redis_client.get(key)
            if json.loads(data).get('type') == 'reading':
                result = json.loads(data)
                break
        return result

    def self_sufficiency(self, meter_id, inhabitants, flat_size):
        """ Calculate a user's self-suffiency value between 0 and 1 where 1
        is optimal and 0 is worst. Self-sufficiency is defined as (inhabitants
        * flat size)/(last energy reading - first energy reading)
        :param str meter_id: the user's meter id
        :param int inhabitants: number of people in the user's flat
        :param float flat_size: the user's flat size
        :return: the user's self-sufficiency value or 0.0 if there are no
        readings for the user
        :rtype: float
        """

        try:
            # Get last reading for user
            last_reading = self.get_last_reading(meter_id)

            # Get first reading for user
            first_reading = self.get_first_reading(meter_id)

            if len(first_reading) == 0 or len(first_reading) == 0:
                logger.error(
                    'No readings for meter id %s in the database.' % meter_id)
                return 0.0

            # Return result
            return (float(inhabitants) *
                    flat_size)/(float(last_reading.get('values').get('energy'))
                                - float(first_reading.get('values').get('energy')))

        except Exception as e:
            message = exception_message(e)
            logger.error(message)
            return 0.0

    def create_data(self, user_id):
        """ Create a data package with the latest available data.
        :param int user_id: the user's id
        :return: the group's overall consumption, the group's overall
        production and each group user's id, meter id, consumption and
        self-sufficiency
        :rtype: dict
        """

        try:
            group_meter_id = get_group_meter_id(user_id)
            group_last_reading = self.get_last_reading(group_meter_id)
            group_users = []

            for member in get_group_members(user_id):
                member_id = member.get('id')
                member_meter_id = member.get('meter_id')
                member_reading = self.get_last_reading(member_meter_id)
                if len(member_reading) == 0:
                    logger.error(
                        'No readings for meter id %s in the database.', member_meter_id)
                    member_consumption = None
                    member_self_sufficiency = None
                else:
                    member_consumption = member_reading.get(
                        'values').get('energy')
                    member_self_sufficiency = self.self_sufficiency(
                        member_meter_id, member.get('inhabitants'), member.get('flat_size'))
                group_users.append(dict(id=member_id, meter_id=member_meter_id,
                                        consumption=member_consumption,
                                        self_sufficiency=member_self_sufficiency))

            if len(group_last_reading) == 0:
                logger.error(
                    'No readings for meter id %s in the database.', group_meter_id)
                group_consumption = None
                group_production = None
            else:
                group_consumption = group_last_reading.get(
                    'values').get('energy')
                group_consumption = group_last_reading.get(
                    'values').get('energy')
            return dict(date=round(datetime.utcnow().timestamp() * 1e3),
                        group_consumption=group_consumption,
                        group_production=group_production,
                        group_users=group_users)

        except Exception as e:
            message = exception_message(e)
            logger.error(message)
            return {}
