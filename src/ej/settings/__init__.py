import logging
import sys

from boogie.configurations import DjangoConf, locales
from .apps import InstalledAppsConf
from .celery import CeleryConf
from .constance import ConstanceConf
from .middleware import MiddlewareConf
from .options import EjOptions
from .paths import PathsConf
from .. import fixes
from .. import services

log = logging.getLogger('ej')


class Conf(locales.brazil(),
           ConstanceConf,
           MiddlewareConf,
           CeleryConf,
           PathsConf,
           DjangoConf,
           InstalledAppsConf,
           EjOptions):
    """
    Configuration class for the EJ platform.

    Settings are created as attributes of a Conf instance and injected in
    the global namespace.
    """

    @property
    def USING_SQLITE(self):
        return 'sqlite3' in self.DATABASE_DEFAULT['ENGINE']

    @property
    def USING_POSTGRES(self):
        return 'postgresql' in self.DATABASE_DEFAULT['ENGINE']

    @property
    def USING_DOCKER(self):
        return False

    AUTH_USER_MODEL = 'ej_users.User'

    # MANAGER CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
    MANAGERS = ADMINS = [
        ('Bruno Martin, Luan Guimarães, Ricardo Poppi, Henrique Parra', 'bruno@hacklab.com.br'),
        ('Laury Bueno', 'laury@hacklab.com.br'),
    ]

    def get_django_templates_dirs(self):
        return [self.SRC_DIR / 'ej/templates/django']

    def get_jinja_templates_dirs(self):
        return [self.SRC_DIR / 'ej/templates/jinja2']

    #
    # Third party modules
    #
    MIGRATION_MODULES = {
        'sites': 'ej.contrib.sites.migrations'
    }

    AUTHENTICATION_BACKENDS = [
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]

    EJ_CONVERSATIONS_URLMAP = {
        'conversation-detail': '/conversations/{conversation.slug}/',
        'conversation-list': '/conversations/',
    }

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
        ),
        'DEFAULT_PERMISSION_CLASSES': (
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 50,
        'DEFAULT_VERSION': 'v1',
    }

    MEDIA_ROOT = "/home2/david/projects/ej-server/local/media"
    STATIC_URL = "/local/media/uploads/"
    DEBUG = True
    STATICFILES_DIRS = ['/home2/david/projects/ej-server/local/media/uploads']
    # REST_AUTH_REGISTER_SERIALIZERS = {
    #     'REGISTER_SERIALIZER': 'ej_users.serializers.RegistrationSerializer'
    # }



Conf.save_settings(globals())

# TODO: Fix this later in boogie configuration stack
# Required for making django debug toolbar work
if ENVIRONMENT == 'local':
    INTERNAL_IPS = [*globals().get('INTERNAL_IPS', ()), '127.0.0.1', '192.168.15.7']

    # Django CORS
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = (
    '192.168.15.7:8081'
    )
    CORS_ORIGIN_REGEX_WHITELIST = (r'^(http://)?localhost:\d{4,5}$',)

    CSRF_TRUSTED_ORIGINS = [
        'localhost:8000',
        'localhost:3000',
        'localhost:8081'
    ]

    X_FRAME_OPTIONS = 'ALLOW-FROM http://localhost:3000'

if ENVIRONMENT == 'production':
    # Django CORS
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_REGEX_WHITELIST = (r'^(https?://)?[\w.]*ejplatform\.org$',)

    CSRF_TRUSTED_ORIGINS = [
        'ejplatform.org',
        'talks.ejplatform.org'
        'dev.ejplatform.org',
        'talks.dev.ejplatform.org',
    ]

    X_FRAME_OPTIONS = 'DENY'

#
# Apply fixes and wait for services to start
#
fixes.apply_all()
services.start_services(sys.modules[__name__])
