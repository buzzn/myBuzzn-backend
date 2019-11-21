from flask import Blueprint, request, jsonify, render_template
from util.error import Error


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

    return 'Hello MyBuzzn!'
