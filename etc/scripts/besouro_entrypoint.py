#!/usr/bin/python

from subprocess import call
import sys

API_TAG = sys.argv[1]
ENVIRONMENT = sys.argv[2]

def start():
    call("git fetch origin %s" % API_TAG, shell=True)
    call("git reset --hard FETCH_HEAD", shell=True)
    call(["sed", "-i", "s#ENVIRONMENT = 'local'#ENVIRONMENT = '%s'# /ej-server/src/ej/settings/__init__.py" % ENVIRONMENT])
    call("pip install -r /ej-server/etc/requirements/production.txt", shell=True)
    call("pip install invoke", shell=True)
    call("VOLATILE_DEPENDENCIES_STRATEGY=unknown pip install -r /ej-server/etc/requirements/git-modules.txt", shell=True)
    call("./manage.py makemigrations --merge --noinput", shell=True)
    call("./manage.py makemigrations", shell=True)
    call("./manage.py migrate", shell=True)
    call("./manage.py collectstatic", shell=True)
    call("inv gunicorn", shell=True)

if __name__ == '__main__':
    start()
