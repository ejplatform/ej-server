#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

printf "\n## Performing Migrations\n\n"

python3 /app/manage.py migrate
# inv db-assets
# inv db-fake --safe
# echo 'production' > /app/local/build.info

printf "\n## Starting Gunicorn\n\n"

/usr/local/bin/gunicorn ej.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app \
    --error-logfile=- \
    --access-logfile=- \
    --log-level info
