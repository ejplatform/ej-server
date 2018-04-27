#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

printf "\n## Starting Server\n\n"

python manage.py migrate
python manage.py runserver_plus 0.0.0.0:8000
