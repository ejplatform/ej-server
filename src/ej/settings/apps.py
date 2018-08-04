from boogie.configurations import InstalledAppsConf as Base
from .options import EjOptions


class InstalledAppsConf(Base, EjOptions):
    project_apps = [
        'ej_boards',
        'ej_clusters',
        'ej_configurations',
        'ej_conversations',
        'ej_clusterviz',
        'ej_dataviz',
        'ej_gamification',
        'ej_help',
        'ej_math',
        'ej_messages',
        'ej_channels',
        'ej_notifications',
        'ej_powers',
        'ej_profiles',
        'ej_reports',
        'ej_users',
        'ej_missions',
        'ej_trophies',
        'ej_candidates'
    ]

    third_party_apps = [
        # External apps created by the EJ team
        # 'courier',
        # 'courier.pushnotifications',
        # 'courier.pushnotifications.providers.onesignal',

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
        'actstream',
        'pinax.points',
        'pinax.badges',
        'constance',
        'constance.backends.database',
        'ckeditor',
        'push_notifications'
    ]

    def get_django_contrib_apps(self):
        apps = super().get_django_contrib_apps()
        return ['django.contrib.staticfiles', 'django.contrib.flatpages', *apps]

    def get_project_apps(self):
        apps = [*super().get_project_apps(), *self.project_apps]
        if self.EJ_ROCKETCHAT_INTEGRATION:
            apps = ['ej_rocketchat', *apps]
        return apps

    def get_third_party_apps(self):
        apps = [*super().get_third_party_apps(), *self.third_party_apps]
        if self.ENVIRONMENT == 'local':
            apps = ['debug_toolbar', *apps, 'django_extensions']
        elif self.ENVIRONMENT == 'production':
            apps = ['raven.contrib.django.raven_compat', 'gunicorn', 'anymail', *apps]
        return apps
