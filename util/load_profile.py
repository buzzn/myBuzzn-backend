import csv
from util.database import db


def run():
    with open('./load_profiles/standardlastprofil-haushalt-2020.csv') as csvfile:
        tbl_reader = csv.reader(csvfile, delimiter=',')
        # for row in tbl_reader:


if __name__ == '__main__':
    run()
