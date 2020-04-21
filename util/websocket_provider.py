from datetime import datetime
import json
import logging.config
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


def get_group_production_meter_ids(user_id):
    """ Get the group production meter ids from the SQLite database for the given user.
    :param int user_id: the user's id
    :returns: the group production meter ids of the group the user belongs to
    :rtype: tuple
    """

    user = db.session.query(User).filter_by(id=user_id).first()
    group = db.session.query(Group).filter_by(id=user.group_id).first()

    return group.group_production_meter_id_first, group.group_production_meter_id_second


def get_group_members(user_id):
    """ Get the parameters from the database to create a group data packet for
    the given user.
    :param int user_id: the user's id
    :return: the group members' ids and inhabitants
    :rtype: [dict]
    """

    user = db.session.query(User).filter_by(id=user_id).first()
    group_users = db.session.query(User).filter_by(
        group_id=user.group_id).all()
    group_members = []
    for group_user in group_users:
        group_members.append(dict(id=group_user.id, meter_id=group_user.meter_id,
                                  inhabitants=group_user.inhabitants))

    return group_members


class WebsocketProvider:
    """ Provides a SocketIO object with live data for the clients. """

    def __init__(self):
        """ Create and setup a websocket provider. """

        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)  # connect to server
        self.cached_first_readings = {}

    def get_sorted_keys(self, meter_id):
        """ Return all keys stored in the redis db for a given meter id.
        :param str meter_id: the meter id to prefix the scan with
        """

        sorted_keys = sorted([key.decode('utf-8') for key in
                              self.redis_client.scan_iter(meter_id + '*')])
        return sorted_keys

    def get_last_reading(self, meter_id):
        """ Return the first meter reading stored in the redis db.
        :param str meter_id: the meter id for which to get the values
        """

        data = self.redis_client.get(meter_id + '_last')

        if data in ({}, []):
            result = dict()
            for key in reversed(self.get_sorted_keys(meter_id)):
                data = self.redis_client.get(key)
                if json.loads(data).get('type') == 'reading':
                    result = json.loads(data)
                    break

        else:
            result = json.loads(data)

        return result

    def get_first_reading(self, meter_id):
        """ Return the first meter reading stored in the redis db.
        :param str meter_id: the meter id for which to get the values
        """
        if meter_id in self.cached_first_readings:
            return self.cached_first_readings[meter_id]

        result = dict()
        for key in self.get_sorted_keys(meter_id):
            data = self.redis_client.get(key)
            if json.loads(data).get('type') == 'reading':
                result = json.loads(data)
                break

        self.cached_first_readings[meter_id] = result
        return result

    def create_member_data(self, member):
        """ Create a data package for a group member to include in a websocket
        data package.
        :param dict member: a group member's parameters
        :return: a group member data package
        :rtype: dict
        """

        member_id = member.get('id')
        member_meter_id = member.get('meter_id')
        member_reading = self.get_last_reading(member_meter_id)
        if len(member_reading) == 0:
            logger.error(
                'No readings for meter id %s in the database.', member_meter_id)
            member_consumption = None
            member_power = None
        else:
            member_consumption = member_reading.get('values').get('energy')
            member_power = member_reading.get('values').get('power')

        member_data = dict(id=member_id,
                           meter_id=member_meter_id,
                           consumption=member_consumption,
                           power=member_power)
        return member_data

    def create_data(self, user_id):
        """ Create a data package with the latest available data.
        :param int user_id: the user's id
        :return: the group's overall consumption, the group's overall
        production and each group user's id, meter id, energy and power
        :rtype: dict
        """

        try:
            group_production_meter_ids = get_group_production_meter_ids(
                user_id)
            group_first_production_meter = group_production_meter_ids[0]
            group_second_production_meter = group_production_meter_ids[1]

            if group_first_production_meter is not None:
                group_last_reading_first_production_meter = self.get_last_reading(
                    group_first_production_meter)
                if len(group_last_reading_first_production_meter) == 0:
                    logger.error(
                        'No readings for group first production meter with id \
                                %s in the database.',
                        group_first_production_meter)
                    group_production_first_meter = 0.0
                else:
                    group_production_first_meter = group_last_reading_first_production_meter.get(
                        'values').get('power')
            else:
                logger.error('No first production meter id for user id %s.',
                             user_id)
                group_production_first_meter = 0.0

            if group_second_production_meter is not None:
                group_last_reading_second_production_meter = self.get_last_reading(
                    group_second_production_meter)
                if len(group_last_reading_second_production_meter) == 0:
                    logger.error(
                        'No readings for group second production meter with id \
                                %s in the database.',
                        group_second_production_meter)
                    group_production_second_meter = 0.0
                else:
                    group_production_second_meter = group_last_reading_second_production_meter.get(
                        'values').get('power')
            else:
                logger.info('No second production meter id for user id %s.',
                            user_id)
                group_production_second_meter = 0.0

            group_users = []
            for member in get_group_members(user_id):
                member_data = self.create_member_data(member)
                group_users.append(member_data)

            group_production = group_production_first_meter + group_production_second_meter

            return dict(date=round(datetime.utcnow().timestamp() * 1e3),
                        group_production=group_production,
                        group_users=group_users)

        except Exception as e:
            message = exception_message(e)
            logger.error(message)
            return {}
