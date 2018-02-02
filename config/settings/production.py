"""
Production Configurations


- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache

- Use sentry for error logging


"""


import logging


from .base import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')


# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/
INSTALLED_APPS += ['raven.contrib.django.raven_compat', ]
RAVEN_MIDDLEWARE = ['raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware']
MIDDLEWARE = RAVEN_MIDDLEWARE + MIDDLEWARE


# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
# END SITE CONFIGURATION

INSTALLED_APPS += ['gunicorn', ]


# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
STATIC_FILES = ROOT_DIR.path('staticfiles')

# Uploaded Media Files
# ------------------------
MEDIA_ROOT = str(STATIC_FILES.path('media'))
MEDIA_URL = '/media/'

# Static Assets
# ------------------------
STATIC_ROOT = str(STATIC_FILES.path('static'))
STATIC_URL = '/static/'

# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='pushtogether <noreply@pushtogether.org.br>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[pushtogether]')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Anymail with Mailgun
INSTALLED_APPS += ['anymail', ]
ANYMAIL = {
    'MAILGUN_API_KEY': env('DJANGO_MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': env('MAILGUN_SENDER_DOMAIN')
}
EMAIL_BACKEND = 'anymail.backends.mailgun.MailgunBackend'

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# CACHING
# ------------------------------------------------------------------------------

# REDIS_LOCATION = '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0)
# # Heroku URL does not pass the DB number, so we parse it in
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_LOCATION,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
#                                         # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
#         }
#     }
# }


# # Sentry Configuration
# SENTRY_DSN = env('DJANGO_SENTRY_DSN')
# SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'root': {
#         'level': 'WARNING',
#         'handlers': ['sentry', ],
#     },
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s '
#                       '%(process)d %(thread)d %(message)s'
#         },
#     },
#     'handlers': {
#         'sentry': {
#             'level': 'ERROR',
#             'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'ERROR',
#             'handlers': ['console', ],
#             'propagate': False,
#         },
#         'raven': {
#             'level': 'DEBUG',
#             'handlers': ['console', ],
#             'propagate': False,
#         },
#         'sentry.errors': {
#             'level': 'DEBUG',
#             'handlers': ['console', ],
#             'propagate': False,
#         },
#         'django.security.DisallowedHost': {
#             'level': 'ERROR',
#             'handlers': ['console', 'sentry', ],
#             'propagate': False,
#         },
#     },
# }
# SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
# RAVEN_CONFIG = {
#     'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
#     'DSN': SENTRY_DSN
# }

# Custom Admin URL, use {% url 'admin:index' %}
ADMIN_URL = env('DJANGO_ADMIN_URL')

# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
