from os import environ
from setup_app import setup_app


class RunConfig():
    """Grabs app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    CLIENT_NAME = 'BuzznClient'


app = setup_app(RunConfig())


if __name__ == "__main__":
    app.run()
