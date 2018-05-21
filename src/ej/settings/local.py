from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
TEMPLATES[1]['OPTIONS']['debug'] = DEBUG

RUNSERVER_PLUS_PRINT_SQL_TRUNCATE = 10**3
SHELL_PLUS_PRINT_SQL_TRUNCATE = 10**3


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

# Django cors - allow requests from any origin in local environment
# ------------------------------------------------------------------------------
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_REGEX_WHITELIST += (r'^(http://)?localhost:\d{4,5}$', )

CSRF_TRUSTED_ORIGINS += [
    'localhost:8000',
    'localhost:3000'
]

X_FRAME_OPTIONS = 'ALLOW-FROM http://localhost:3000'
