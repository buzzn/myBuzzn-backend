import json
from os import environ
from threading import Lock
import eventlet
from flask import render_template, Response, request, session
from flask_api import status
from flask_socketio import SocketIO, emit
from models.user import User
from setup_app import setup_app
from util.database import db
from util.error import NO_METER_ID
from util.websocket_provider import WebsocketProvider
from models.user import User


eventlet.monkey_patch()


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
thread = None
thread_lock = Lock()
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
wp = WebsocketProvider()
clients = {}


@app.route('/live', methods=['GET'])
def live():
    meter_id = request.args.get('meter_id', default=None, type=str)
    if meter_id is None:
        return NO_METER_ID.to_json(), status.HTTP_400_BAD_REQUEST
    session['meter_id'] = meter_id
    return Response(render_template('live.html'))


def background_thread():
    """ Emit server-generated live data to the clients every 60s. """
    while True:
        socketio.sleep(60)
        with app.app_context():
            for key in clients:
                user = db.session.query(User).filter_by(
                    meter_id=clients[key].get('meter_id')).first()
                message = json.dumps(wp.create_data(user.id))
                socketio.emit(
                    'live_data', {'data': message}, namespace='/live', room=key)


@socketio.on('connect', namespace='/live')
def connect():
    # We need the global statement here, cf.
    # https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/example/app.py
    # pylint: disable=global-statement
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    clients[request.sid] = {'meter_id': session['meter_id']}
    emit('live_data', {'data': 'Connected with sid ' +
                               request.sid}, room=request.sid)


@socketio.on('disconnect', namespace='/live')
def disconnect():
    del clients[request.sid]


def run_server():
    """Starts the app on port 5000.
       This api call can used to start the app from another python script.
    """
    socketio.run(app, port=5000)


if __name__ == "__main__":
    socketio.run(app, debug=True)
