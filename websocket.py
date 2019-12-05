import logging
from threading import Lock
from datetime import datetime, timedelta
from flask_socketio import SocketIO


logger = logging.getLogger(__name__)

# pylint: disable=fixme
# TODO - Set/get user ID in/from database (user)
# TODO - Set/get group meter IDs in/from database (other users and their meter
# IDs from group)
# TODO - Set/get people in flat in/from database
# TODO - Set/get flat size in/from database
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

    def self_sufficiency(self, meter_id, inhabitants, flat_size):
        """ Calculate a user's self-suffiency value the past year as a value
        between 0 and 1 where 1 is optimal and 0 is worst. Self-sufficiency is
        defined as (inhabitants * flat size)/(energy value today - energy
        value one year ago)
        :param str meter_id: the user's meter id
        :param int inhabitants: number of people in the user's flat
        :param float flat_size: the user's flat size
        :return: the user's self-sufficiency value, 0.0 if there is no history
        :rtype: float
        """

        now = round(datetime.now().timestamp() * 1e3)
        begin = round((datetime.now() - timedelta(days=365)).timestamp() * 1e3)

        try:
            # Get energy value today
            individual_last_reading = self.d.get_last_reading(meter_id)
            energy_today = individual_last_reading.get('values').get('energy')

            # Get energy value one year ago
            individual_first_reading = self.d.get_readings(meter_id, begin, now,
                                                           'one_year')
            energy_one_year_ago = individual_first_reading[0].get(
                'values').get('energy')

            # Return result
            return (float(inhabitants) * flat_size)/(float(energy_today)
                                                     - float(energy_one_year_ago))

        except Exception as e:
            logger.error("Exception: %s", e)

            # Return result
            return 0.0

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

            self.self_sufficiency(user_id, meter_id)
            return dict(date=now,
                        groupConsumption=groupConsumption,
                        groupProduction=groupProduction,
                        selfSufficiency=self.self_sufficiency(
                            user_id, meter_id),
                        usersConsumption=usersConsumption)

        except Exception as e:
            logger.error("Exception: %s", e)
            return {}
