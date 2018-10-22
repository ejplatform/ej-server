#!/usr/bin/env bash

if [ -z $VIRTUAL_ENV ]; then
    echo "ERROR: configuration should run inside a virtual env"
    echo "If you have virtualenvwrapper installed, run 'mkvirtualenv ej -p /usr/bin/python3'"
    exit
fi
echo "Installing chromedriver..."
# sh etc/scripts/chromedriver.sh
pip install invoke
inv configure --silent
