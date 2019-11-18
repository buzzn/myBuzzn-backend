from os import environ

from flask import Flask

app = Flask(__name__)

# Config
app.config.update({
    'SECRET_KEY': environ.get('SECRET_KEY'),
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
})

if __name__ == "__main__":
    app.run()
