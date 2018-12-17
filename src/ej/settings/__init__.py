import logging

from boogie.configurations import DjangoConf, env
from ej.settings.dramatiq import DramatiqConf
from .apps import InstalledAppsConf
from .constance import ConstanceConf
from .email import EmailConf
from .log import LoggingConf
from .middleware import MiddlewareConf
from .notifications import NotificationsConf
from .options import EjOptions
from .paths import PathsConf
from .security import SecurityConf
from .themes import ThemesConf
from .. import fixes

log = logging.getLogger('ej')


class Conf(ThemesConf,
           ConstanceConf,
           MiddlewareConf,
           NotificationsConf,
           DramatiqConf,
           SecurityConf,
           LoggingConf,
           PathsConf,
           InstalledAppsConf,
           DjangoConf,
           EjOptions,
           EmailConf):
    """
    Configuration class for the EJ platform.

    Settings are created as attributes of a Conf instance and injected in
    the global namespace.
    """

    USING_DOCKER = env(False, name='USING_DOCKER')
    HOSTNAME = env('localhost')

    #
    # Accounts
    #
    AUTH_USER_MODEL = 'ej_users.User'
    ACCOUNT_AUTHENTICATION_METHOD = 'email'
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_UNIQUE_EMAIL = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    LOGIN_REDIRECT_URL = '/'
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
    # ACCOUNT_EMAIL_VERIFICATION = 'none'
    SOCIALACCOUNT_PROVIDERS = {
        'facebook': {
            'SCOPE': ['email'],
            'METHOD': 'oauth2'
        }
    }

    # MANAGER CONFIGURATION
    # See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
    MANAGERS = ADMINS = [
        ('Bruno Martin, Luan Guimarães, Ricardo Poppi, Henrique Parra', 'bruno@hacklab.com.br'),
        ('Laury Bueno', 'laury@hacklab.com.br'),
    ]

    #
    # Third party modules
    #
    MIGRATION_MODULES = {
        'sites': 'ej.contrib.sites.migrations'
    }

    EJ_CONVERSATIONS_URLMAP = {
        'conversation-detail': '/conversations/{conversation.slug}/',
        'conversation-list': 'conversation:list',
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

<<<<<<< HEAD
    SESSION_COOKIE_DOMAIN = '.pencillabs.com.br'
    ALLOWED_HOSTS = ['127.0.0.1', '.pencillabs.com.br']
=======
    #this settings must be anabled only on production.
    #SESSION_COOKIE_DOMAIN = '.ejplatform.org'

    ALLOWED_HOSTS = ['127.0.0.1', '.ejplatform.org', '.ejparticipe.com.br', '.pencillabs.com.br']

>>>>>>> de342c9c... Use middleware for login redirect.
    # REST_AUTH_REGISTER_SERIALIZERS = {
    #     'REGISTER_SERIALIZER': 'ej_users.serializers.RegistrationSerializer'
    # }

    # Use this variable to change the ej environment during the docker build step.
    ENVIRONMENT = 'local'
    DEFAULT_FROM_EMAIL = "Empurrando Juntos <noreply@mail.ejplatform.org>"

    def get_email_backend(self):
        if self.ENVIRONMENT == 'production':
            self.ANYMAIL = {'MAILGUN_API_KEY': ''}
            return 'anymail.backends.mailgun.EmailBackend'
        else:
            return 'django.core.mail.backends.console.EmailBackend'


Conf.save_settings(globals())

#
# Apply fixes and wait for services to start
#
fixes.apply_all()
