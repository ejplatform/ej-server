#!/bin/bash                                                                     
set -e                                                                          

echo "Creating user $USER_PG @ postgres"
psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
  \set ej_user `echo $USER_PG`
  \set ej_db `echo $DB_PG`
  \set ej_password `echo $PASSWORD_PG`
  CREATE USER :ej_user WITH CREATEDB PASSWORD ':ej_password';
  CREATE DATABASE :ej_db;
  GRANT ALL PRIVILEGES ON DATABASE :ej_db TO :ej_user;
EOSQL

echo "host all all 0.0.0.0/0 trust" >>  "$PGDATA/pg_hba.conf"
