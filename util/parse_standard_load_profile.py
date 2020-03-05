import csv
from datetime import datetime, date, time
import logging
import logging.config
import argparse
import pytz
from models.loadprofile import LoadProfileEntry
from util.database import create_session


logging.config.fileConfig(fname='logger_configuration.conf', disable_existing_loggers=False)
logger = logging.getLogger('util/parse_standard_load_profile')
exception_template = "An exception of type {0} occurred. Arguments:\n{1!r}"


def parse_args():
    usage = "Parse a standard load profile in csv format and upload it to the\
    sqlite database mybuzzn.db. Run it like this from project root: \'python\
    util/parse_standard_load_profile.py path/to/standardlastprofil.csv\'. Please make sure\
    your csv file has a header row and does not contain any duplicate values.\
    Consider the file 'util/standardlastprofil-haushalt-2020-bereinigt.csv' on\
    how to structure your values."

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('filepath', type=str, help='the csv file path')
    args = vars(parser.parse_args())
    return args


# pylint: disable=too-many-locals
def run():

    csvfile_path = parse_args().get('filepath')
    with open(csvfile_path) as csvfile:
        tbl_reader = csv.reader(csvfile, delimiter=',')
        next(tbl_reader, None)
        session = create_session()
        tz_local = pytz.timezone('Europe/Berlin')
        try:
            for row in tbl_reader:
                _date = row[0].split('/')
                _time = row[1].split(':')
                year = int(_date[2])
                month = int(_date[0])
                day = int(_date[1])
                hours = int(_time[0])
                minutes = int(_time[1])
                seconds = int(_time[2])
                date_formatted = datetime.combine(date(year, month, day),
                                                  time(hours, minutes,
                                                       seconds))
                date_local = tz_local.localize(date_formatted)
                date_global = date_local.astimezone(pytz.utc)
                energy = row[2]
                session.add(LoadProfileEntry(date_global.strftime('%Y-%m-%d'),
                                             date_global.strftime('%H:%M:%S'), energy))
            session.commit()

        except Exception as e:
            message = exception_template.format(type(e).__name__, e.args)
            logger.error(message)


if __name__ == '__main__':
    run()
