import csv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.schema import MetaData
# from util.database import db
from models.loadprofile import LoadProfile


def create_session():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    print(engine.table_names())
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def run():
    with open('./load_profiles/standardlastprofil-haushalt-2020.csv') as csvfile:
        # tbl_reader = csv.reader(csvfile, delimiter=',')
        session = create_session()

        session.execute(LoadProfile.insert(), {"date": "1/1/2020", "time":
                                               "0:15:00", "energy": 27.135})

        # for row in tbl_reader:


if __name__ == '__main__':
    run()
