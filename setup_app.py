from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask import Flask

from routes.consumption_history import IndividualConsumptionHistory
from routes.consumption_history import GroupConsumptionHistory
from routes.disaggregation import IndividualDisaggregation
from routes.disaggregation import GroupDisaggregation
from routes.set_password import SetPassword
from routes.reset_password import ResetPassword
from routes.login import Login

from util.database import db
from util.error import UNKNOWN_RESOURCE


def setup_app(app_config):
    """Create an app using the given config.
    :param object app_config: An object containing all the environmental
    parameters.
    :return: The created app, ready to run.
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

    # Flask migrate needs those to create migrations files.
    # pylint: disable=import-outside-toplevel,unused-import
    from models.user import User
    from models.group import Group
    Migrate(app, db)

    # Login stuff
    JWTManager(app)

    # Routes are called by the user, there are actually used.
    # Register routes
    app.register_blueprint(IndividualConsumptionHistory)
    app.register_blueprint(GroupConsumptionHistory)
    app.register_blueprint(IndividualDisaggregation)
    app.register_blueprint(GroupDisaggregation)
    app.register_blueprint(Login)
    app.register_blueprint(ResetPassword)
    app.register_blueprint(SetPassword)

    # Routes are called by the user, so they are actually used.
    #pylint: disable=unused-variable
    @app.errorhandler(404)
    def not_found(error):
        return (UNKNOWN_RESOURCE.to_json(),
                error.code)

    return app
