#!/bin/bash
# start.sh

export FLASK_ASSETS="./assets"


export SECRET_KEY="12345once I court a ghish al1v3"
export FLASK_APP=wsgi.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=config.py
flask run
