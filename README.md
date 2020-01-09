# MyBuzzn backend
An app to investigate your power consumption habits for *BUZZN* customers.

## How to run
We recommend to setup a virtual env for the projects' requirements.
```bash
cd PROJECT_ROOT
virtualenv -p `whereis python | cut -d ' ' -f3` .venv
source .venv/bin/activate
```
Install the requirements
```bash
pip install -r "requirements.txt"
pip install git+https://github.com/buzzn/discovergy.git
```
The following environment variables need to be set:
```bash
EMAIL
PASSWORD
BUZZN_SQLALCHEMY_DATABASE_URI    # Indicates where the database is stored
BUZZN_SECRET_KEY                 # Security ussues like session data
BUZZN_PASSWORD_SALT              # The salt for the users' passwords
BUZZN_SMTP_SERVER                # SMTP server to use for sending mails
BUZZN_EMAIL                      # The email used to send mails from the backend
BUZZN_EMAIL_PASSWORD             # Mailpassword of the mailaccount
BUZZN_BASE_URL                   # Baseurl of the backend i.e. address.
                                 # Everyhing which needs to be in front of the
                                 # api calls. Example mybuzzn-backend.buzzn.net
REDIS_HOST			 # Indicates where the redis database is stored
REDIS_PORT			 # The port to access the redis database, usually 6379
REDIS_DB			 # The redis database 

```

Starting the app: 
```bash
python app.py
```
Currently the webserver is running in development mode to restart after source 
code changes. To change this behaviour, set the parameter `debug` to `False` in the
`socketio.run()` call in `app.py`.

Starting the worker to populate and periodically update the redis db with metering
data from discovergy: 
```bash
python util/task.py
```
Make sure to run it from the root directory, otherwise it cannot access the SQLite
database properly.

## Project structure
```
project root
├── migrations    # Database migration stuff
├── models        # Data-Models
├── routes        # Defines the http api
├── templates     # HTML templates for specific app routes and testing purposes
├── tests         # Unittests
├── util          # Misc. db interaction, error handling, translations, mailing, websocket interaction, eventlet tasks
└── app.py        # The app-main.
```

## Database
To access the database, the app reads the database's address from the
environment variable `BUZZN_SQLALCHEMY_DATABASE_URI`.
The database structure is created using migrations. A migration is a
script which transforms the database between two consecutive versions
(i.e. git revisions) of the app.  The model classes (usually stored in
`/models`) model the entities used by the app and provide methods to
load and store them in from/in the database.  To generate the
according tables given a new model use the _flask migrate_ method:
`flask db migrate` generates a new migration file in
`/migrations/versions` to transform the databse structure to meet the models'
needs. To apply the migrations run `flask db upgrade`.

## Redis server 
The metering data periodially obtained from discovergy is stored in a Redis database, 
so you need to have a Redis server running. On Linux, you can likely get it as a 
package through your operating system's package manager (e.g. `sudo pacman -S redis`). 
You will not need to interact with Redis at all outside of just ensuring that 
the service is running (e.g. `sudo systemctl start redis.service; redis-cli ping`).

## Running the tests
Set environment variables
```bash
source ./setup_testing_environment.sh
```
Run tests
```bash
python -m unittest
```

## Linter
```bash
pylint app.py apitests models routes tests util
```
