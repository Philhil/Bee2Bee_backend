# Bee2Bee Backend
## Setup local dev environment
Prerequisites:
* python 3.8
    * with pip and virtualenv

Setup:
* cd $repo
* python3 -m virtualenv venv
* Linux: source venv/bin/activate
* Windows: venv/bin/activate.bat
* pip install -r requirements.txt
* cd src
* FLASK_APP=flask_entry flask run
* api is reachable via  http://127.0.0.1:5000/