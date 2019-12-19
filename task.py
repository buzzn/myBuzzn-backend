import time
import eventlet

eventlet.monkey_patch()


def populate_redis(discovergy_handler, redis_db):
    """ Populate the redis database with all discovergy data from the past. """

    # Flush all keys from server
    redis_db.flushdb()
    print('Populating redis database with all discovergy data from the past.')


def update_redis(discovergy_handler, redis_db):
    """ Update the redis database every 60s with the latest discovergy data. """

    while True:
        time.sleep(60)
        print('Updating redis database with the latest discovergy data.')
