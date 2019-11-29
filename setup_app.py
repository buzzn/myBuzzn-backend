from flask import Flask
from routes.consumption_history import IndividualConsumptionHistory
from routes.consumption_history import GroupConsumptionHistory
from routes.disaggregation import IndividualDisaggregation
from routes.disaggregation import GroupDisaggregation

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

    # Register routes
    app.register_blueprint(IndividualConsumptionHistory)
    app.register_blueprint(GroupConsumptionHistory)
    app.register_blueprint(IndividualDisaggregation)
    app.register_blueprint(GroupDisaggregation)

    # Routes are called by the user, they are actually used.
    # pylint: disable=unused-variable
    @app.errorhandler(404)
    def not_found(error):
        return (UNKNOWN_RESSOURCE.to_json(),
                error.code)

    return app
