# MyBuzzn backend
An app to investigate your power consumption habits for *BUZZN* customers.

## How to run
We recommend to setup a virtual environment for the projects' requirements.
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
## Calculating Code Coverage
Install Coverage.py
```bash
pip install coverage
```
Calculate code coverage
```bash
coverage run -m unittest
```
All unittests are run and the code coverage is calculated. 

Show code coverage report
```bash
coverage report -m
```
## Linter
```bash
pylint app.py apitests models routes tests util
```
##Logfile
Replace the logfile in the logger_configuration with a suitable logfile for production.

## How to deploy
This chapter describes how to get a production instance running.
### Setup a new instance
Clone the sources:
```bash
git clone https://github.com/buzzn/mybuzzn-backend.git
```
We recommend to setup a virtual environment for the projects' requirements.
```bash
cd PROJECT_ROOT
virtualenv -p `whereis python | cut -d ' ' -f3` .venv
source .venv/bin/activate
```
Install the python requirements
```bash
pip install -r "requirements.txt"
pip install git+https://github.com/buzzn/discovergy.git
```

Now create a systemd service `mybuzzn-backend.service`, which starts the socketio server we use to run
the app in:
```ini
[Unit]
Description=Run mybuzzn-backend as an flask socketio instance.

[Service]
WorkingDirectory=/var/www/mybuzzn-backend.buzzn.net/mybuzznbackend
ExecStart=/var/www/mybuzzn-backend.buzzn.net/mybuzznbackend/env/bin/python mybuzzn-backend.py
After=network.target
User=mybuzznbackend
Group=mybuzznbackend

[Install]
WantedBy=multi-user.target
```
Either store it on /etc/systemd/system/ or create a link there pointing to it.
Start it with `systemctl start mybuzzn-backend.service`.

Create an endpoint in your webserver, for example for nginx, create a new
server in `/etc/nginx/sites-available/mybuzzn-backend.net`
```
server {
    listen 80;
    server_name mybuzzn-backend.buzzn.net

    error_log /var/www/mybuzzn-backend.buzzn.net/logs/error.log warn;
    access_log /var/www/mybuzzn-backend.buzzn.net/logs/access.log combined;


    # This is where our socketio server should respond
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    # This is where the websocket should respond
    location /socket.io {
        include proxy_params;

        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:5000/socket.io;
    }
}
```
And create a link from `/etc/nginx/sites-enable/mybuzzn-backend.net` pointing to
it. Then restart nginx `systemctl restart nginx`

Make sure a file `setup_environment.py` exists in the project root which sets
environment variables like this:
```python
import os

os.environ['BUZZN_SECRET_KEY'] = '...'
os.environ['DISCOVERGY_EMAIL'] = '...'
os.environ['DISCOVERGY_PASSWORD'] = '...'
os.environ['JWT_SECRET_KEY'] = '...'
os.environ['BUZZN_SQLALCHEMY_DATABASE_URI'] = '...'
os.environ['BUZZN_PASSWORD_SALT'] = '...'
os.environ['BUZZN_SMTP_SERVER'] = '...'
os.environ['BUZZN_SMTP_SERVER_PORT'] = '...'
os.environ['BUZZN_EMAIL'] = '...'
os.environ['BUZZN_EMAIL_PASSWORD'] = '...'
os.environ['BUZZN_BASE_URL'] = '...'
os.environ['BUZZN_MAILER'] = '...'
os.environ['REDIS_HOST'] = '...'
os.environ['REDIS_PORT'] = '...'
os.environ['REDIS_DB'] = '...'
```

Make you have a running instance of redis `systemctl start redis.service` and
the `start_redis_task.py` is running. If you are running systemd, this can be
done using a service:
```ini
[Unit]
Description=Fill redis db with current reading values
After=network.target redis.service

[Service]
Type=simple
Reastart=always
WorkingDirectory=/var/www/mybuzzn-backend.buzzn.net/mybuzznbackend
ExecStart=/var/www/mybuzzn-backend.buzzn.net/mybuzznbackend/env/bin/python start_redis_task.py
StandardOutput=journal
User=mybuzznbackend
Group=mybuzznbackend

[Install]
WantedBy=multi-user.target⏎
```

### Upgrading to a new version
To upgrade to a new version, go to the project root and run `git pull`.
If something has changed in the database models, run `source ./venv/bin/activate` to
activate the python environment. Then run `./flask db upgrade` to
upgrade the database.

Finally restart the the web server and the redis task which fills the redis database with meter
readings:
`systemctl restart apache2.service redis-task.service mybuzzn-backend.service`

