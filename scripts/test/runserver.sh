#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

printf "\n## Performing Migrations\n\n"

python3 manage.py migrate

printf "\n## Starting Server\n\n"

python3 manage.py runserver_plus 0.0.0.0:8000
