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
BUZZN_SQLALCHEMY_DATABASE_URI
BUZZN_SECRET_KEY
```

Starting a flask server: `./.venv/bin/flask run`

If you want the webserver to restart after source code changes, run it in
development mode:
```bash
FLASK_DEBUG=1 ./.venv/bin/flask run
```

## Project structure
```
project root
├── apitests      # Api tests go here
├── migrations    # Database migration stuff
├── models        # Data-Models
├── routes        # Defines the http api
├── tests         # Unittests
├── util          # Misc. db interaction, error handling
└── app.py        # The app-main.
```

## Database
The database structure is created using migrations. A migration is a
script which transforms the database between two consecutive versions
(i.e. git revisions) of the app.  The model classes (usually stored in
`/models`) model the entities used by the app and provide methods to
load and store them in from/in the database.  To generate the
according tables given a new model use the _flask migrate_ method:
`flask db migrate` generates a new migration file in
`/migrations/versions` to transform the databse structure to meet the models'
needs. To apply the migrations run `flask db upgrade`.

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

