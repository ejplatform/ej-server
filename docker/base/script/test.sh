#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

printf "\n## Performing Migrations\n\n"

python manage.py migrate

printf "\n## Performing Tests\n\n"

pytest
