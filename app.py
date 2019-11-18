from os import environ

from flask_api.status import status

from setup_app import setup_app
from util.error import Error

class RunConfig():
    """Graps app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get('BUZZN_SQLALCHEMY_DATABASE_URI')
    PASSWORD_SALT = environ.get('PASSWORD_SALT')
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
    OAUTH2_REFRESH_TOKEN_GENERATOR = True


app = setup_app(RunConfig())

# Routes
@app.errorhandler(404)
def not_found(error):
    return (Error('Unknown path', 'This ressource is not available. '+error).to_json(),
            status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    app.run()
