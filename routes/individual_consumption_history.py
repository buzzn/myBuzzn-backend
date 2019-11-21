from discovergy.discovergy import Discovergy
from flask import Blueprint
from datetime import datetime, date


client_name = 'BuzznClient'
email = 'team@localpool.de'
password = 'Zebulon_4711'
meter_id = 'b4234cd4bed143a6b9bd09e347e17d34'


IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)


@IndividualConsumptionHistory.route('/individual-consumption-history')
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval.
    :param str begin: start time of consumption, default is today at 0:00
    :param str end: end time of consumption, default is
    datetime.datetime.now()
    :param str resolution: time distance between returned readings with
    possible values 'raw', 'three_minutes', 'fifteen_minutes', 'one_hour',
    'one_day', 'one_week', 'one_month', 'one_year', default is 'three_minutes'
    :return: (200, array of float values where each one stands for the total power
    consumed at the time) or (204, {}) if there is no history
    :rtype: TODO
    """

    # Set meter ID in database

    # Get meter ID from database

    # Put Discovergy credentials into environment variables

    # Use the given parameters

    # Call discovergy API for the given meter
    d = Discovergy(client_name)
    d.login(email, password)
    start = round(datetime.combine(datetime.now(),
                                   datetime.min.time()).timestamp() * 1e3)
    readings = d.get_readings(meter_id, start, 'three_minutes')

    # Return value array

    return 'Hello MyBuzzn!'
