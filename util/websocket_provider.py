from datetime import datetime
import json
import logging
import os
import redis
from models.group import Group
from models.user import User
from util.database import db


logger = logging.getLogger(__name__)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_db = os.environ['REDIS_DB']


def get_parameters(user_id):
    """ Get the parameters from the database to create data packet for the
    given user.
    :param int user_id: the user's id
    :return: meter_id, group_meter_id, [{str => int, str => str}, ...],
    inhabitants, flat_size
    :rtype: tuple
    """

    user = db.session.query(User).filter_by(id=user_id).first()
    group = db.session.query(Group).filter_by(id=user.group_id).first()
    group_users = db.session.query(User).filter_by(
        group_id=user.group_id).filter(User.id.isnot(user_id)).all()
    group_members = []
    for group_user in group_users:
        group_members.append(
            dict(id=group_user.id, meter_id=group_user.meter_id))
    return user.meter_id, group.group_meter_id, group_members, user.inhabitants, user.flat_size


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
        """ Return the first meter reading stored in the redis db. """

        return json.loads(self.redis_client.get(self.get_sorted_keys(meter_id)[-1]))

    def get_first_reading(self, meter_id):
        """ Return the first meter reading stored in the redis db. """

        return json.loads(self.redis_client.get(self.get_sorted_keys(meter_id)[0]))

    def self_sufficiency(self, meter_id, inhabitants, flat_size):
        """ Calculate a user's self-suffiency value between 0 and 1 where 1
        is optimal and 0 is worst. Self-sufficiency is defined as (inhabitants
        * flat size)/(last energy reading - first energy reading)
        :param str meter_id: the user's meter id
        :param int inhabitants: number of people in the user's flat
        :param float flat_size: the user's flat size
        :return: the user's self-sufficiency value, 0.0 if there is no history
        :rtype: float
        """

        try:
            # Get last energy value
            last_energy_value = self.get_last_reading(meter_id).get('energy')

            # Get first energy value
            first_energy_value = self.get_first_reading(meter_id).get('energy')

            # Return result
            return (float(inhabitants) * flat_size)/(float(last_energy_value) -
                                                     float(first_energy_value))

        except Exception as e:
            logger.error("Exception: %s", e)

            # Return result
            return 0.0

    def create_data(self, user_id):
        """ Create a data package with the latest available data.
        :param int user_id: the user's id
        :return: {str => int, str => int, str => int, str => float, str => {str
        => int, str => int}}
        :rtype: dict
        """

        now = round(datetime.now().timestamp() * 1e3)

        try:
            meter_id, group_meter_id, group_members, inhabitants, flat_size = get_parameters(
                user_id)
            group_last_reading = self.get_last_reading(group_meter_id)
            individual_last_reading = self.get_last_reading(meter_id)
            usersConsumption = []
            usersConsumption.append(dict(
                id=user_id, consumption=individual_last_reading.get('energy')))
            for member in group_members:
                reading = self.get_last_reading(member.get('meter_id'))
                usersConsumption.append(dict(id=member.get('id'),
                                             consumption=reading.get('energy')))
            return dict(date=now,
                        groupConsumption=group_last_reading.get('energy'),
                        groupProduction=group_last_reading.get('energyOut'),
                        selfSufficiency=self.self_sufficiency(
                            meter_id, inhabitants, flat_size),
                        usersConsumption=usersConsumption)

        except Exception as e:
            logger.error("Exception: %s", e)
            return {}
