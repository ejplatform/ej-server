from boogie.configurations import InstalledAppsConf as Base
from .options import EjOptions


class InstalledAppsConf(Base, EjOptions):
    project_apps = [
        # Math
        'ej_math',
        'ej_reports',
        'ej_clusters',

        # Conversations
        'ej_boards',
        'ej_conversations',

        # Core apps
        'ej_help',
        'ej_configurations',
        'ej_profiles',
        'ej_users',
    ]

    third_party_apps = [
        # Third party apps
        'taggit',
        'rules',
        'crispy_forms',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.twitter',
        'allauth.socialaccount.providers.github',
        'allauth.socialaccount.providers.google',
        'django_filters',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_auth',
        'rest_auth.registration',
        'corsheaders',
        'constance',
        'constance.backends.database',
    ]

    def get_django_contrib_apps(self):
        apps = super().get_django_contrib_apps()
        return ['django.contrib.flatpages', *apps]

    def get_project_apps(self):
        apps = [*super().get_project_apps(), *self.project_apps]
        if self.EJ_ROCKETCHAT_INTEGRATION:
            print('Rocket.Chat integration is ON')
            apps = ['ej_rocketchat', *apps]
        return apps

    def get_third_party_apps(self):
        apps = [*super().get_third_party_apps(), *self.third_party_apps]
        if self.ENVIRONMENT == 'local':
            apps = ['debug_toolbar', *apps, 'django_extensions']
        elif self.ENVIRONMENT == 'production':
            apps = ['raven.contrib.django.raven_compat', 'gunicorn', 'anymail', *apps]
        return apps
