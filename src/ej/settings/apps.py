from boogie.configurations import InstalledAppsConf as Base, env

from .options import EjOptions


class InstalledAppsConf(Base, EjOptions):
    """
    This class contains a registry of installed applications
    that stores configuration.
    It also maintains a list of available models.
    """
    USE_DJANGO_ADMIN = env(True, name="{attr}")
    DISABLE_DJANGO_DEBUG_TOOLBAR = env(True, name="{attr}")

    project_apps = [
        # Gamification
        "ej_gamification",
        "ej_experiments",
        # Notifications
        # 'ej_notifications',
        # Boards
        "ej_boards",
        # Math
        "ej_clusters",
        "ej_dataviz",
        # Core apps
        "ej_profiles",
        "ej_conversations",
    ]

    third_party_apps = [
        "boogie.apps.fragments",
        "taggit",
        "rules",
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        "allauth.socialaccount.providers.facebook",
        "allauth.socialaccount.providers.twitter",
        "allauth.socialaccount.providers.google",
        # 'allauth.socialaccount.providers.github',
        "ej_users",
        # 'django_filters',
        "rest_framework",
        # 'rest_framework.authtoken',
        # 'rest_auth',
        # 'rest_auth.registration',
        'constance',
        'constance.backends.database',
        # 'push_notifications',
    ]

    def get_django_contrib_apps(self):
        """
        Return the contrib apps
        """
        return [*super().get_django_contrib_apps(), "django.contrib.flatpages"]

    def get_project_apps(self):
        """
        This is used to return the project apps in the init
        :return: middleware
        """
        apps = [*super().get_project_apps(), *self.project_apps]
        if self.EJ_ROCKETCHAT_INTEGRATION:
            print("Rocket.Chat integration is ON")
            apps = ["ej_rocketchat", *apps]
        return apps

    def get_third_party_apps(self):
        """
        This is used to return the third party apps in the init
        :return: third_party_apps
        """
        apps = [*super().get_third_party_apps(), *self.third_party_apps]
        if self.ENVIRONMENT == "local":
            if self.DISABLE_DJANGO_DEBUG_TOOLBAR:
                apps = [*apps, "django_extensions"]
            else:
                apps = ["debug_toolbar", *apps, "django_extensions"]

        elif self.DEBUG and not self.DISABLE_DJANGO_DEBUG_TOOLBAR:
            apps = ["debug_toolbar", *apps]
        if self.ENVIRONMENT == "production":
            # "raven.contrib.django.raven_compat" ?
            # "anymail"?
            apps = ["gunicorn", *apps]
        return apps
