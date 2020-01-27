import csv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.loadprofile import LoadProfile


def create_session():
    parent_dir = Path(__file__).parent.parent.absolute()
    dbPath = str(parent_dir) + '/mybuzzn.db'
    engine = create_engine('sqlite:///%s' % dbPath)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def run():
    with open('./load_profiles/standardlastprofil-haushalt-2020.csv') as csvfile:
        tbl_reader = csv.reader(csvfile, delimiter=',')
        next(tbl_reader, None)
        session = create_session()
        for row in tbl_reader:
            session.add(LoadProfile(row[0], row[1], float(row[2])))
            session.commit()


if __name__ == '__main__':
    run()
