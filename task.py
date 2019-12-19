import time
import eventlet
from flask import current_app as app
from models.user import User
from util.database import db as sqlite_db

eventlet.monkey_patch()


def populate_redis(discovergy_handler, redis_db):
    """ Populate the redis database with all discovergy data from the past. """

    # Flush all keys from server
    redis_db.flushdb()

    with app.app_context:

        # Get all meter ids from database
        users = sqlite_db.session.query(User).all()
        print(type(users))
        print(users)

        # Get all group meter ids from database


def update_redis(discovergy_handler, redis_db):
    """ Update the redis database every 60s with the latest discovergy data. """

    while True:
        time.sleep(60)
        print('Updating redis database with the latest discovergy data.')
