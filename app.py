from os import environ

from setup_app import setup_app


class RunConfig():
    """Grabs app parameters from the environment."""
    SECRET_KEY = environ.get('BUZZN_SECRET_KEY')
    CLIENT_NAME = 'BuzznClient'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = environ.get('BUZZN_SQLALCHEMY_DATABASE_URI')
    PASSWORD_SALT = environ.get('BUZZN_PASSWORD_SALT')
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    BUZZN_SMTP_SERVER = environ.get('BUZZN_SMTP_SERVER')
    BUZZN_SMTP_SERVER_PORT = environ.get('BUZZN_SMTP_SERVER_PORT')
    BUZZN_EMAIL = environ.get('BUZZN_EMAIL')
    BUZZN_EMAIL_PASSWORD = environ.get('BUZZN_EMAIL_PASSWORD')
    BUZZN_BASE_URL = environ.get('BUZZN_BASE_URL')
    BUZZN_MAILER = environ.get('BUZZN_MAILER')

app = setup_app(RunConfig())

if __name__ == "__main__":
    app.run()
