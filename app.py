from os import environ

from setup_app import setup_app

from routes.consumption_history import IndividualConsumptionHistory
from routes.consumption_history import GroupConsumptionHistory

class RunConfig():
    """Graps app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')


app = setup_app(RunConfig())

# Routes
app.register_blueprint(IndividualConsumptionHistory)
app.register_blueprint(GroupConsumptionHistory)

if __name__ == "__main__":
    app.run()
