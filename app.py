from os import environ

from flask import Flask

app = Flask(__name__)

# Config
app.config.update({
    'SECRET_KEY': environ.get('BUZZN_SECRET_KEY')
})

if __name__ == "__main__":
    app.run()
