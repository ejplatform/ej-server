"""
Local settings

- Run in Debug mode

- Use console backend for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

RUNSERVER_PLUS_PRINT_SQL_TRUNCATE = 10**7
SHELL_PLUS_PRINT_SQL_TRUNCATE = 10**7

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='!Xng`w:eusr3h~3{RL7BF3jgE8p.liKe73*{q@/Amr!;c4*}-k')

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_PORT = 1025

EMAIL_HOST = 'localhost'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.console.EmailBackend')


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost',])

import socket
import os
# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + '1']

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# django-extensions and math module
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions', 'pushtogether_math']

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Django cors - allow requests from any origin in local environment
# ------------------------------------------------------------------------------
CORS_ORIGIN_WHITELIST += (
    'localhost:8000',
    'localhost:3000',
)
CORS_ORIGIN_ALLOW_ALL = True

CSRF_TRUSTED_ORIGINS += (
    'localhost:8000',
    'localhost:3000'
)

X_FRAME_OPTIONS = 'ALLOW-FROM http://localhost:3000'
