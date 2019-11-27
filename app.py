from os import environ
from setup_app import setup_app
from routes.consumption_history import IndividualConsumptionHistory
from routes.consumption_history import GroupConsumptionHistory
from routes.disaggregation import IndividualDisaggregation
from routes.disaggregation import GroupDisaggregation


class RunConfig():
    """Graps app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    CLIENT_NAME = 'BuzznClient'


app = setup_app(RunConfig())

# Routes
app.register_blueprint(IndividualConsumptionHistory)
app.register_blueprint(GroupConsumptionHistory)
app.register_blueprint(IndividualDisaggregation)
app.register_blueprint(GroupDisaggregation)

if __name__ == "__main__":
    app.run()
