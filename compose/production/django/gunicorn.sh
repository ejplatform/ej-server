#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# the official postgres image uses 'postgres' as default user if not set explictly.
if [ -z "$POSTGRES_USER" ]; then
    export POSTGRES_USER=postgres
fi

export DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres:5432/$POSTGRES_USER

python /app/manage.py collectstatic --noinput

python /app/manage.py migrate

/usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app \
    --error-logfile=- \
    --access-logfile=- \
    --log-level debug
