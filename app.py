import json
import logging
from os import environ
from os import path
import logging.config
from threading import Lock
import eventlet
from flask import render_template, Response, request, session, jsonify
from flask_api import status
from flask_socketio import SocketIO, emit
from flask_swagger import swagger
# from swagger_ui import api_doc
from setup_app import setup_app
from util.database import db
from util.error import NO_METER_ID, exception_message
from util.websocket_provider import WebsocketProvider
from models.user import User


eventlet.monkey_patch()
logger = logging.getLogger(__name__)


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


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'util/logger_configuration.conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
app = setup_app(RunConfig())
thread = None
thread_lock = Lock()
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
wp = WebsocketProvider()
clients = {}


@app.route("/spec/swagger.json")
def spec():
    swag = swagger(app, from_file_keyword='swagger_from_file')
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "myBuzzn App API"
    swag['info']['description'] = "An app to investigate your power " \
                                  "consumption habits for BUZZN customers."

    return jsonify(swag)


@app.route('/live', methods=['GET'])
def live():
    """ swagger_from_file: swagger_files/get_live.yml """
    meter_id = request.args.get('meter_id', default=None, type=str)
    if meter_id is None:
        return NO_METER_ID.to_json(), status.HTTP_400_BAD_REQUEST
    session['meter_id'] = meter_id
    return Response(render_template('live.html'))


def background_thread():
    """ Emit server-generated live data to the clients every 60s. """
    while True:
        with app.app_context():
            for key in dict(clients):
                try:
                    user = db.session.query(User).filter_by(
                        meter_id=clients[key].get('meter_id')).first()
                    message = json.dumps(wp.create_data(user.id))
                    socketio.emit('live_data', {'data': message},
                                  namespace='/live', room=key)
                except Exception as e:
                    message = exception_message(e)
                    logger.error(message)
                    del clients[key]
            socketio.sleep(20)

@socketio.on('connect', namespace='/live')
def connect():
    # We need the global statement here, cf.
    # https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/example/app.py
    # pylint: disable=global-statement
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    meter_id = request.args.get('meter_id', default=None, type=str)
    if meter_id is None:
        meter_id = session['meter_id']
    clients[request.sid] = {'meter_id': meter_id}
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
    #config_path = path.join(path.dirname(path.abspath(__file__)), 'swagger_files/swagger.json')
    #api_doc(app, config_path=config_path,
    #        url_prefix='/api/doc', title='myBuzzn App API')

    socketio.run(app, debug=True)
