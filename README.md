# MyBuzzn backend
An app to investigate your power consumption habits for *BUZZN* customers.

## How to run
We recommend to setup a virtual env for the projects requirements.
```bash
cd PROJECT_ROOT
virtualenv -p `whereis python | cut -d ' ' -f3)` env
```
Install the requirements
```bash
pip install -r "requirements.txt"
```
Starting a flask server: `./env/bin/flask run`

If you want the webserver to restart after source code changes, run it in
development mode:
```bash
FLASK_DEBUG=1 ./env/bin/flask run
````

## Linter
```bash
./env/bin/pylint app.py
```