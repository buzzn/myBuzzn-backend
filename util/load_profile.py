import csv
import logging
import argparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.loadprofile import LoadProfile


logging.basicConfig()
logger = logging.getLogger('util/load_profile')
logging.getLogger().setLevel(logging.INFO)
exception_template = "An exception of type {0} occurred. Arguments:\n{1!r}"


def create_session():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def parse_args():
    usage = """Parse a standard load profile in csv format and upload it to the sqlite
database mybuzzn.db. Run it like this from project root:

    python util/load_profile.py -filepath 'util/standardlastprofil-haushalt-2020-bereinigt.csv'

Please make sure your csv file has a header row and does not contain any duplicate values.
"""

    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('filepath', type=str, nargs='+',
                        help='the csv file path')
    args = vars(parser.parse_args())
    return args


def run():

    csvfile_path = parse_args().get('filepath')
    with open(csvfile_path[0]) as csvfile:
        tbl_reader = csv.reader(csvfile, delimiter=',')
        next(tbl_reader, None)
        session = create_session()
        try:
            for row in tbl_reader:
                session.add(LoadProfile(row[0], row[1], float(row[2])))
            session.commit()

        except Exception as e:
            message = exception_template.format(type(e).__name__, e.args)
            logger.error(message)


if __name__ == '__main__':
    run()
