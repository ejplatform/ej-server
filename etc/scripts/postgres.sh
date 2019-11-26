#!/usr/bin/env bash

echo "Starting postgres container"
echo "ATTENTION! This container is *INSECURE* and should only be used during development."
echo ""
echo "Data will be stored at local/db/pgsql/"
echo ""
echo "Please export DJANGO_DB_URL=psql://ej:ej@localhost:5432/ej"
echo ""

mkdir -p local/db/pgsql
sudo docker run -e POSTGRES_DB=ej -e POSTGRES_USER=ej -e POSTGRES_PASSWORD=ej -p 5432:5432 -v `$pwd`/local/db/pgsql postgres:10-alpine
sudo chown $USER local/db/pgsql -Rv
