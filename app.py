from os import environ

from flask import Flask

from routes.individual_consumption_history import IndividualConsumptionHistory

app = Flask(__name__)

# Config
app.config.update({
    'SECRET_KEY': environ.get('SECRET_KEY'),
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
})

# Routes
app.register_blueprint(IndividualConsumptionHistory)

if __name__ == "__main__":
    app.run()
