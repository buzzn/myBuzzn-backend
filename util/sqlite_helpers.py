from datetime import datetime, timedelta, time
from os import path
import logging.config
from models.baseline import BaseLine
from models.group import Group
from models.per_capita_consumption import PerCapitaConsumption
from models.savings import UserSaving, CommunitySaving
from models.user import User
from util.date_helpers import calc_support_year_start_datetime, message_timestamp
from util.energy_saving_calculation import calc_energy_consumption_last_term,\
    calc_estimated_energy_saving
from util.error import exception_message
from util.per_capita_consumption_calculation import define_base_values, calc_per_capita_consumption


log_file_path = path.join(path.dirname(
    path.abspath(__file__)), 'logger_configuration.conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def get_all_meter_ids(session):
    """ Get all meter ids from the SQLite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]\
        + [group_meter_id[0]
           for group_meter_id in session.query(Group.group_meter_id).all()]\
        + [group_production_meter_id_first[0] for
           group_production_meter_id_first in
           session.query(Group.group_production_meter_id_first).all()]\
        + [group_production_meter_id_second[0] for group_production_meter_id_second
           in session.query(Group.group_production_meter_id_second).all()]


def get_all_users(session):
    """ Get all users from the SQLite database. """

    return session.query(User).all()


def get_all_user_meter_ids(session):
    """ Get all user meter ids from sqlite database. """

    return [meter_id[0] for meter_id in session.query(User.meter_id).all()]


def write_savings(session):
    """ Write the energy savings of each user and the community to the
    SQLite database.
    """

    start = calc_support_year_start_datetime()
    try:
        for key, value in estimate_energy_saving_each_user(start,
                                                           session).items():

            if value is None:
                message = """Cannot calculate saving for meter id {} on {}
                because last term\'s energy consumption or estimated energy
                consumption is missing. Writing 0.0 instead""".format(key,
                                                                      message_timestamp)
                logger.info(message)

                # Create UserSaving instance and set saving to 0.0
                user_saving = UserSaving(datetime.utcnow(), key, 0.0)

            else:
                user_saving = UserSaving(datetime.utcnow(), key, value)

            session.add(user_saving)

        # Create CommunitySaving instance
        community_saving = estimate_energy_saving_all_users(start, session)
        session.add(CommunitySaving(datetime.utcnow(), community_saving))

        session.commit()
    except Exception as e:
        message = exception_message(e)
        logger.error(message)


def write_baselines(session):
    """ Write the baseline for each user to the SQLite database. """

    start = calc_support_year_start_datetime()
    try:
        for meter_id in get_all_user_meter_ids(session):
            baseline = calc_energy_consumption_last_term(meter_id, start)

            if baseline is None:
                message = """Cannot write baseline for meter id {} on {} because last term\'s energy
                consumption is missing""".format(meter_id, message_timestamp)
                logger.info(message)

            else:
                # Create BaseLine instance
                session.add(BaseLine(datetime.utcnow(), meter_id, baseline))

        session.commit()
    except Exception as e:
        message = exception_message(e)
        logger.error(message)


def write_base_values_or_per_capita_consumption(session):
    """ If yesterday was the start of the support year, write the base values
    for all users to the SQLite database.
    Otherwise, write yesterday's per capita consumption for all users to the SQLite database.
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    """

    yesterday_date = (datetime.today() - timedelta(days=1)).date()
    today_date = datetime.today().date()
    _time = time(0, 0, 0)
    yesterday = datetime.combine(yesterday_date, _time)
    today = datetime.combine(today_date, _time)
    support_year_start = calc_support_year_start_datetime()

    if today == support_year_start:
        write_base_values(yesterday, session)
    else:
        write_per_capita_consumption(yesterday, session)


def write_base_values(dt, session):
    """ Write the base values for each user to the SQLite database.
    :param datetime dt: the date to write the values for
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    """

    for user in get_all_users(session):
        base_values = define_base_values(user.inhabitants, dt)

        # Create PerCapitaConsumption instance
        session.add(PerCapitaConsumption(dt, user.meter_id, base_values['consumption'],
                                         base_values['consumption_cumulated'],
                                         base_values['inhabitants'],
                                         base_values['per_capita_consumption'],
                                         base_values['per_capita_consumption_cumulated'],
                                         base_values['days'],
                                         base_values['moving_average'],
                                         base_values['moving_average_annualized']))

    session.commit()


def write_per_capita_consumption(dt, session):
    """ Write the per capita consumption for each user to the SQLite database.
    If for one user there are no yesterday's values in the database, write the
    base values for that user.
    If today's entry already exists for a user, skip writing that entry.
    :param datetime dt: the date to write the values for
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    """

    for user in get_all_users(session):

        try:
            # Check if entry exists
            pcc_today = session.query(PerCapitaConsumption).filter_by(
                date=dt, meter_id=user.meter_id).first()

            # Create today's entry if it does not exist
            if not pcc_today:
                dataset = calc_per_capita_consumption(
                    user.meter_id, user.inhabitants, dt, session)

                # If there are no yesterday's values in the database for this user,
                # define the base values
                if dataset is None:
                    dataset = define_base_values(user.inhabitants, dt)

            # Create PerCapitaConsumption instance
                session.add(PerCapitaConsumption(dt, user.meter_id, dataset['consumption'],
                                                 dataset['consumption_cumulated'],
                                                 dataset['inhabitants'],
                                                 dataset['per_capita_consumption'],
                                                 dataset['per_capita_consumption_cumulated'],
                                                 dataset['days'],
                                                 dataset['moving_average'],
                                                 dataset['moving_average_annualized']))
        except Exception as e:
            message = exception_message(e)
            logger.error(message)

    session.commit()


def estimate_energy_saving_each_user(start, session):
    """ Calculate the estimated energy saving for each user.
    :param datetime.date start: the start date of the given term
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    :returns: the estimated energy saving of each user mapped to their meter id in the given term
    :rtype: dict
    """

    savings = dict()
    for meter_id in get_all_user_meter_ids(session):
        saving = calc_estimated_energy_saving(meter_id, start)
        savings[meter_id] = saving

    return savings


def estimate_energy_saving_all_users(start, session):
    """ Calculate the estimated energy saving of all users by summing up all
    last term energy consumptions and subtracting all estimated energy
    consumptions.
    :param datetime.date start: the start date of the given term
    :param sqlalchemy.orm.scoping.scoped_session session: the database session
    :returns: the estimated energy saving of all users in the given term
    :rtype: float
    """

    savings = 0.0
    for meter_id in get_all_user_meter_ids(session):
        saving = calc_estimated_energy_saving(meter_id, start)
        if saving is not None:
            savings += saving

    return savings
