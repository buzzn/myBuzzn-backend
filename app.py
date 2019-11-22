from os import environ

from flask import Flask

from util.error import Error

app = Flask(__name__)

# Config
app.config.update({
    'SECRET_KEY': environ.get('BUZZN_SECRET_KEY')
})

# Routes
@app.errorhandler(404)
def not_found(error):
    return (Error('Unknown path', 'This ressource is not available. '+error).to_json(),
            status.HTTP_404_NOT_FOUND)

if __name__ == "__main__":
    app.run()
