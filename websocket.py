import logging
import os
from threading import Lock
from datetime import datetime, date
from flask import jsonify
from flask_socketio import SocketIO


logger = logging.getLogger(__name__)


class Websocket:
    """ Websocket to handle asynchronous emitting of live data to the
    clients. """

    def __init__(self, app, async_mode, d):
        self._async_mode = async_mode
        self.thread = None
        self.thread_lock = Lock()
        self.socketio = SocketIO(app, async_mode=self._async_mode)
        self.d = d

    def create_data(self):
        """ Creates a data package with the latest discovergy readings. """

        # pylint: disable=fixme
        # TODO - Set/get meter ID in/from database (user meter)
        # TODO - Set/get group meter ID in/from database (common meter)
        # TODO - Set/get user ID in/from database (user)
        # TODO - Set/get group IDs in/from database (other users from group)
        # TODO - Set/get group meter IDs in/from database (other users' meters)
        group_ids = {{"id": 1, "meter_id": '52d7c87f8c26433dbd095048ad30c8cf'},
                     {"id": 2, "meter_id": '117154df05874f41bfdaebcae6abfe98'}}

        now = round(datetime.now().timestamp() * 1e3)
        year = datetime.today().year
        begin = round(datetime(year, 1, 1).timestamp() * 1e3)
        try:
            group_last_reading = self.d.get_last_reading(
                os.environ['GROUP_METER_ID'])
            groupConsumption = group_last_reading.get('values').get('energy')
            groupProduction = group_last_reading.get('values').get('energyOut')
            individual_first_reading = self.d.get_readings(
                os.environ['METER_ID'], begin, now, 'one_year')
            individual_last_reading = self.d.get_last_reading(
                os.environ['METER_ID'])
            selfSufficiency = individual_last_reading.get(
                'energy') - individual_first_reading.get('values').get('energy')
            usersConsumption = []
            usersConsumption.append(dict(
                id=os.environ['USER_ID'], consumption=individual_last_reading.get('values').get('energy')))
            for user in group_ids:
                reading = self.d.get_last_reading(
                    user.get('meter_id'))
                usersConsumption.append(dict(id=user.get('id'),
                                             consumption=reading.get('values').get('energy')))
            data = dict(date=date, groupConsumption=groupConsumption,
                        groupProduction=groupProduction,
                        selfSufficiency=selfSufficiency, usersConsumption=usersConsumption)
            return jsonify(data)

        except Exception as e:
            logger.error("Exception: %s", e)
            return jsonify({})
