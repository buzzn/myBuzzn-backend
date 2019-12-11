import logging
from threading import Lock
from datetime import datetime, timedelta
from flask_socketio import SocketIO
from models.user import User
from models.group import Group
from util.database import db


logger = logging.getLogger(__name__)


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


class Websocket:
    """ Websocket to handle asynchronous emitting of live data to the
    clients. """

    def __init__(self, app, async_mode, d):
        self._async_mode = async_mode
        self.thread = None
        self.thread_lock = Lock()
        self.socketio = SocketIO(app, async_mode=self._async_mode)
        self.d = d
        self.users = db.session.query(User).all()

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

    # pylint: disable=fixme
    # TODO - Set/get user ID in/from database (user)
    def create_data(self, user_id):
        """ Creates a data package with the latest discovergy readings.
        :param int user_id: the user's id
        :return: {str => int, str => int, str => int, str => float, str => {str
        => int, str => int}}
        :rtype: dict
        """

        now = round(datetime.now().timestamp() * 1e3)
        try:
            meter_id, group_meter_id, group_members, inhabitants, flat_size = get_parameters(
                user_id)
            group_last_reading = self.d.get_last_reading(group_meter_id)
            individual_last_reading = self.d.get_last_reading(meter_id)
            usersConsumption = []
            usersConsumption.append(dict(id=user_id,
                                         consumption=individual_last_reading.
                                         get('values').get('energy')))
            for member in group_members:
                reading = self.d.get_last_reading(member.get('meter_id'))
                usersConsumption.append(dict(id=member.get('id'),
                                             consumption=reading.get('values').get('energy')))

            return dict(date=now,
                        groupConsumption=group_last_reading.get(
                            'values').get('energy'),
                        groupProduction=group_last_reading.get(
                            'values').get('energyOut'),
                        selfSufficiency=self.self_sufficiency(
                            meter_id, inhabitants, flat_size),
                        usersConsumption=usersConsumption)

        except Exception as e:
            logger.error("Exception: %s", e)
            return {}

    def background_thread(self):
        """ Emit server-generated live data every 60s to the clients. """
        while True:
            self.socketio.sleep(60)

            for user in self.users:
                live_data = self.generate_data(user.id)
                self.socketio.emit('live_data',
                                   {'data': live_data},
                                   namespace='ws:/live')
