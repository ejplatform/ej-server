import os
import time
import psycopg2

def get_environment_variable(variable):
    default_value = "postgres"
    value = os.getenv(variable, default_value)
    if(value == default_value):
        print(f"Using default value for {variable}")
    return value

def wait_for_postgres(dbname, user, password, host):
    try:
        conn = psycopg2.connect(
            dbname = dbname,
            user = user,
            password = password,
            host = host
        )
    except psycopg2.OperationalError:
        return False
    return True

dbname = get_environment_variable("POSTGRES_DB")
user = get_environment_variable("POSTGRES_USER")
password = get_environment_variable("POSTGRES_PASSWORD")
host = get_environment_variable("POSTGRES_HOST")

while(not wait_for_postgres(dbname, user, password, host)):
    print("Postgres is unavailable. Retrying in 1 second...")
    time.sleep(1)

print("Postgres is available. Continuing...")
