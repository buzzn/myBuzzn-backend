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

## Running the tests
```bash
python -m unittest
```

## Linter
```bash
./.venv/bin/pylint app.py apitests models routes tests util
```
