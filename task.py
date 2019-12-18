import eventlet
import time


eventlet.monkey_patch()


def populate_redis():
    """ Populate the redis database with all discovergy data from the past. """

    print('Populating redis database with all discovergy data from the past.')


def update_redis():
    """ Update the redis database every 60s with the latest discovergy data. """
    while True:
        time.sleep(60)
        print('Updating redis database with the latest discovergy data.')
