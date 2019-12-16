import json
from os import environ
from threading import Lock
from flask import render_template, Response, request
from flask_socketio import SocketIO, emit
from discovergy.discovergy import Discovergy
# from models.user import User
from setup_app import setup_app
# from util.database import db
from websocket_provider import WebsocketProvider


class RunConfig():
    """Grabs app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    CLIENT_NAME = 'BuzznClient'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get('BUZZN_SQLALCHEMY_DATABASE_URI')
    PASSWORD_SALT = environ.get('BUZZN_PASSWORD_SALT')
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    BUZZN_SMTP_SERVER = environ.get('BUZZN_SMTP_SERVER')
    BUZZN_SMTP_SERVER_PORT = environ.get('BUZZN_SMTP_SERVER_PORT')
    BUZZN_EMAIL = environ.get('BUZZN_EMAIL')
    BUZZN_EMAIL_PASSWORD = environ.get('BUZZN_EMAIL_PASSWORD')
    BUZZN_BASE_URL = environ.get('BUZZN_BASE_URL')
    BUZZN_MAILER = environ.get('BUZZN_MAILER')


app = setup_app(RunConfig())
d = Discovergy(app.config['CLIENT_NAME'])
thread = None
thread_lock = Lock()
socketio = SocketIO(app, async_mode='eventlet')
wp = WebsocketProvider()
clients = []


@app.route('/live', methods=['GET', 'POST'])
def live():
    meter_id = request.args.get('meter_id', default='', type=str)
    print('Meter id: %s' % meter_id)
    return Response(render_template('live.html', async_mode=socketio.async_mode))


def background_thread():
    """ Emit server-generated live data to the clients every 60s. """
    while True:
        socketio.sleep(60)
        with app.app_context():

            # pylint: disable=fixme
            # TODO - emit data for user with param meter id
            # TODO - update in broker api
            # users = db.session.query(User).all()
            # for user in users:
                # message = json.dumps(wp.create_data(user.id))

            message = json.dumps({
                "date": 3152997594059,
                "groupConsumption": 2015853400000,
                "groupProduction": 2189063000,
                "selfSufficiency": 0.0,
                "usersConsumption": [
                    {"id": 1,
                     "consumption": 3544858992189000},
                    {"id": 2,
                     "consumption": 188036451474000},
                    {"id": 3,
                     "consumption": 1494461436564000}]
            })
            socketio.emit('live_data', {'data': message}, namespace='/live')


@socketio.on('connect', namespace='/live')
def test_connect():
    # We need the global statement here, cf.
    # https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/example/app.py
    # pylint: disable=global-statement
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    print('Client with session id %s connected' % str(request.sid))
    emit('live_data', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/live')
def test_disconnect():
    print('Client with session id %s disconnected' % str(request.sid))


if __name__ == "__main__":
    socketio.run(app, debug=True)
