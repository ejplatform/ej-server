#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


printf "\n## Building css"
sass /app/lib/scss/maindefault.scss:/app/lib/assets/css/maindefault.css

printf "\n## Starting Server\n\n"
inv i18n -c
python3 manage.py runserver_plus 0.0.0.0:8000
