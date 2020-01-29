import csv
import logging
import argparse
from models.loadprofile import LoadProfileEntry
from util.database import create_session


logging.basicConfig()
logger = logging.getLogger('util/load_profile')
logging.getLogger().setLevel(logging.INFO)
exception_template = "An exception of type {0} occurred. Arguments:\n{1!r}"


def parse_args():
    usage = """Parse a standard load profile in csv format and write it to the
    sqlite database mybuzzn.db. Run it like this from project root: \'python
    util/load_profile.py path/to/standardlastprofil.csv\'. Please make sure
    your csv file has a header row and does not contain any duplicate values.
    Consider the file 'util/standardlastprofil-haushalt-2020-bereinigt.csv' on
    how to structure your values.
    """

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('filepath', type=str, help='the csv file path')
    args = vars(parser.parse_args())
    return args


def run():
    """ Parse a standard load profile in csv format and write it to the sqlite
    database mybuzzn.db. """

    try:
        csvfile_path = parse_args().get('filepath')
        with open(csvfile_path) as csvfile:
            tbl_reader = csv.reader(csvfile, delimiter=',')
            next(tbl_reader, None)
            session = create_session()
            for row in tbl_reader:
                date = row[0]
                time = row[1]
                energy = row[2]
                session.add(LoadProfileEntry(date, time, energy))
            session.commit()

    except Exception as e:
        message = exception_template.format(type(e).__name__, e.args)
        logger.error(message)


if __name__ == '__main__':
    run()
