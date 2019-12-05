import logging
from threading import Lock
from datetime import datetime, timedelta
from flask import jsonify
from flask_socketio import SocketIO


logger = logging.getLogger(__name__)

# pylint: disable=fixme
# TODO - Set/get meter ID in/from database (user meter)
# TODO - Set/get group meter ID in/from database (common meter)
# TODO - Set/get user ID in/from database (user)
# TODO - Set/get group meter IDs in/from database (other users and their meter
# IDs from group)
# TODO - discovergy login


class Websocket:
    """ Websocket to handle asynchronous emitting of live data to the
    clients. """

    def __init__(self, app, async_mode, d):
        self._async_mode = async_mode
        self.thread = None
        self.thread_lock = Lock()
        self.socketio = SocketIO(app, async_mode=self._async_mode)
        self.d = d

    def self_sufficiency(self, user_id, meter_id):
        """ Calculate the self-suffiency value for the given user. """

        now = round(datetime.now().timestamp() * 1e3)
        begin = round((datetime.now() - timedelta(days=365)).timestamp() * 1e3)
        individual_first_reading = self.d.get_readings(
            meter_id, begin, now, 'one_month')

        return 0.5

    def create_data(self, meter_id, group_meter_id, user_id, group_meter_ids):
        """ Creates a data package with the latest discovergy readings. """

        now = round(datetime.now().timestamp() * 1e3)
        try:
            group_last_reading = self.d.get_last_reading(group_meter_id)
            groupConsumption = group_last_reading.get('values').get('energy')
            groupProduction = group_last_reading.get('values').get('energyOut')
            individual_last_reading = self.d.get_last_reading(meter_id)
            usersConsumption = []
            usersConsumption.append(dict(id=user_id,
                                         consumption=individual_last_reading.
                                         get('values').get('energy')))
            for user in group_meter_ids:
                reading = self.d.get_last_reading(user.get('meter_id'))
                usersConsumption.append(dict(id=user.get('id'),
                                             consumption=reading.get('values').get('energy')))
            data = dict(date=now,
                        groupConsumption=groupConsumption,
                        groupProduction=groupProduction,
                        selfSufficiency=self.self_sufficiency(
                            user_id, meter_id),
                        usersConsumption=usersConsumption)
            print(data)
            print(jsonify(data))
            return jsonify(data)

        except Exception as e:
            logger.error("Exception: %s", e)
            return jsonify({})
