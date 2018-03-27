from ..core import env, DEBUG

#
# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Raises ImproperlyConfigured exception if database variables aren't in os.environ
USE_SQLITE = env.bool('USE_SQLITE', default=False)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': env('POSTGRES_HOST', default='postgres'),
            'NAME': env('POSTGRES_DB', default='ej'),
            'USER': env('POSTGRES_USER', default='ej'),
            'PASSWORD': env('POSTGRES_PASSWORD', default='ej'),
            'ATOMIC_REQUESTS': True,
        },
    }
