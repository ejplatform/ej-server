#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

printf "\n## Performing Migrations\n\n"

python3 manage.py migrate

printf "\n## Performing Tests\n\n"

pytest --cov
