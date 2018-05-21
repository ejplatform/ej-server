from boogie.configurations import InstalledAppsConf as Base
from .options import EjOptions


class InstalledAppsConf(Base, EjOptions):
    PROJECT_APPS = [
        # Inner EJ apps
        'ej_gamification.apps.GamificationConfig',
        'ej_configurations.apps.ConfigurationsConfig',
        'ej_profiles.apps.EjProfilesConfig',

        # Independent EJ Apps
        'ej_conversations.apps.EjConversationsConfig',
        'ej_users',
    ]

    THIRD_PARTY_APPS = [
        # External apps created by the EJ team
        'courier',
        'courier.pushnotifications',
        'courier.pushnotifications.providers.onesignal',

        # Third party apps
        'crispy_forms',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.twitter',
        'django_filters',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_auth',
        'rest_auth.registration',
        'corsheaders',
        'captcha',
        'actstream',
        'pinax.points',
        'pinax.badges',
        'constance',
        'constance.backends.database',
    ]

    def get_django_contrib_apps(self):
        apps = super().get_django_contrib_apps()
        return ['django.contrib.flatpages', *apps]

    def get_project_apps(self):
        apps = super().get_project_apps()
        if self.EJ_ENABLE_ROCKETCHAT:
            apps = ['ej_rocketchat.apps.EJRocketchatConfig', *apps]
        return apps

    def get_third_party_apps(self):
        apps = super().get_third_party_apps()
        if self.ENVIRONMENT == 'local':
            apps = ['debug_toolbar', *apps, 'django_extensions']
        elif self.ENVIRONMENT == 'production':
            apps = ['raven.contrib.django.raven_compat', 'gunicorn', 'anymail', *apps]
        return apps
