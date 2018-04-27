#!/usr/bin/env bash

set -o errexit
set -o pipefail

if [ ! -z $MANUAL_MODE ] && $MANUAL_MODE; then
    echo
    echo "[WARNING] Manual mode active"
    echo "[WARNING] You can execute commands direct by docker[-compose] exec"
    echo
    sleep infinity
else
    set -o nounset
    python /app/manage.py migrate
    /usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app \
        --error-logfile=- \
        --access-logfile=- \
        --log-level info
fi
