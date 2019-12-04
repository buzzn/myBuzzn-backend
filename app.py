from os import environ
from discovergy.discovergy import Discovergy
from websocket import Websocket
from setup_app import setup_app


class RunConfig():
    """Grabs app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    CLIENT_NAME = 'BuzznClient'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get('BUZZN_SQLALCHEMY_DATABASE_URI')


app = setup_app(RunConfig())
d = Discovergy(app.config['CLIENT_NAME'])

if __name__ == "__main__":
    websocket = Websocket(app, "eventlet", d)
    websocket.socketio.run(app)
