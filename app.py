from os import environ

from setup_app import setup_app

class RunConfig():
    """Graps app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')

app = setup_app(RunConfig())

if __name__ == "__main__":
    app.run()
