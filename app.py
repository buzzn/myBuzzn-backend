from os import environ
from setup_app import setup_app


class RunConfig():
    """Grabs app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    CLIENT_NAME = 'BuzznClient'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get('BUZZN_SQLALCHEMY_DATABASE_URI')

app = setup_app(RunConfig())


if __name__ == "__main__":
    app.run()
