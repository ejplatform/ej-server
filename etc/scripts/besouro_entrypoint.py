#!/usr/bin/python

from subprocess import call
import sys

API_TAG = sys.argv[1]
ENVIRONMENT = sys.argv[2]

def start():
    call("git fetch origin %s" % API_TAG, shell=True)
    call("git reset --hard FETCH_HEAD", shell=True)
    call(["sed", "-i", "s#ENVIRONMENT = 'local'#ENVIRONMENT = '%s'#" % ENVIRONMENT,  "/ej-server/src/ej/settings/__init__.py"])
    call(["sed", "-i", "s#'MAILGUN_API_KEY': ''#'MAILGUN_API_KEY': 'd707cd161665327e0378975e37972307-770f03c4-814b27bd'#", "/ej-server/src/ej/settings/__init__.py"])
    call(["sed", "-i", "s#'FCM_API_KEY': ''#'FCM_API_KEY': 'AAAAPfbSOIA:APA91bGGxsuM5hHsufW_KXxCw9I7BZ4Vc1eunpvtFO2Huvk9w_2DSJB8FCPqq61-4Dnyb5xUH5wHvvh0y7FYGppJIs0VK0fpY9HskbrnWDXhwbTjkdHMJv1dS8_XmWoN6gkjFpAyjIaT'#", "/ej-server/src/ej/settings/__init__.py"])
    call("pip install -r /ej-server/etc/requirements/production.txt", shell=True)
    call("pip install invoke", shell=True)
    call("VOLATILE_DEPENDENCIES_STRATEGY=unknown pip install -r /ej-server/etc/requirements/git-modules.txt", shell=True)
    call("./manage.py migrate --noinput", shell=True)
    call("./manage.py collectstatic --noinput", shell=True)
    call("inv gunicorn", shell=True)

if __name__ == '__main__':
    start()
