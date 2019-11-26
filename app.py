from os import environ

from flask import Flask

from routes.individual_consumption_history import IndividualConsumptionHistory
from routes.group_consumption_history import GroupConsumptionHistory

app = Flask(__name__)

# Config
app.config.update({
    'SECRET_KEY': environ.get('BUZZN_SECRET_KEY')
})

# Routes
app.register_blueprint(IndividualConsumptionHistory)
app.register_blueprint(GroupConsumptionHistory)

if __name__ == "__main__":
    app.run()
