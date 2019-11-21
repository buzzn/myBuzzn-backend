from flask import Blueprint, request


IndividualConsumptionHistory = Blueprint('IndividualConsumptionHistory',
                                         __name__)


@IndividualConsumptionHistory.route('/individual-consumption-history')
def individual_consumption_history():
    """ Shows the history of consumption of the given time interval.
    :param str begin: start time of consumption, default is today at 0:00
    :param str end: end time of consumption, default is
    datetime.datetime.now()
    :param int tics: interval time in seconds, default is 60
    :return: (200, array of float values where each one stands for the total power
    consumed at the time) or (204, {}) if there is no history
    :rtype: TODO
    """

    # Get meter ID from database

    # Call discovergy API for the given meter

    # Return value array

    return 'Hello MyBuzzn!'
