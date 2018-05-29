#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

cmd="$@"

printf "\n## Verifying PostgreSQL Connection\n\n"
python3 /wait_for_postgres.py

exec $cmd
