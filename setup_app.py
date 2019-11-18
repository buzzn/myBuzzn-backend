from flask_jwt_extended import (JWTManager, jwt_required)
from flask_migrate import Migrate
from flask_api import status
from flask import Flask

from routes.create_user import CreateUser
from routes.set_password import SetPassword
from routes.login import Login
from util.database import db
from flask import Flask
from models.user import User

from util.error import UNKNOWN_RESSOURCE


def setup_app(app_config):
    """Create an app using the given config.

    Arguments:
        app_config {object} -- An object containing all the environmental
        parameters.

    Returns:
        flask app -- The created app, ready to run.
    """
    app = Flask(__name__)
    app.config.from_object(app_config)

    class JsonDefault(app.response_class):
        """This is a backend talking json, so json should be the default
        mimetype. """

        def __init__(self, *args, **kwargs):
            super(JsonDefault, self).__init__(*args, **kwargs)
            self.mimetype = 'application/json'

    app.response_class = JsonDefault

    # Models
    db.init_app(app)
    Migrate(app, db)

    # Login stuff
    JWTManager(app)

    # Routes are called by the user, there are actually used.
    #pylint: disable=unused-variable
    @app.errorhandler(404)
    def not_found(error):
        return (UNKNOWN_RESSOURCE.to_json(),
                error.code)

    app.register_blueprint(Login)
    app.register_blueprint(SetPassword)

    @app.route('/protected')
    @jwt_required
    def protected():
        return 'got me'

    @app.route('/users')
    def users():
        return '\n'.join(x.get_name() + " " + str(x.get_activation_token())
                     + " " + str(x.get_status()) + " " +
                     str(x.get_role()) + " "
                     + str(x._password) for x in User.query.all())
    return app
