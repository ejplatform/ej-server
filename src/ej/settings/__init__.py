from boogie.configurations import DjangoConf, locales
from .apps import InstalledAppsConf
from .celery import CeleryConf
from .constance import ConstanceConf
from .middleware import MiddlewareConf
from .options import EjOptions
from .paths import PathsConf
from .. import fixes


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
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ),
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 50,
        'DEFAULT_VERSION': 'v1',
    }

    # REST_AUTH_REGISTER_SERIALIZERS = {
    #     'REGISTER_SERIALIZER': 'ej_users.serializers.RegistrationSerializer'
    # }


Conf.save_settings(globals())
fixes.apply_all()
