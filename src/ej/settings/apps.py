from boogie.configurations import InstalledAppsConf as Base, env

from .options import EjOptions


class InstalledAppsConf(Base, EjOptions):
    USE_DJANGO_ADMIN = env(True, name="{name}")

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
    from allauth import account

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
        # 'constance',
        # 'constance.backends.database',
        # 'push_notifications',
    ]

    def get_django_contrib_apps(self):
        return [*super().get_django_contrib_apps(), "django.contrib.flatpages"]

    def get_project_apps(self):
        apps = [*super().get_project_apps(), *self.project_apps]
        if self.EJ_ROCKETCHAT_INTEGRATION:
            print("Rocket.Chat integration is ON")
            apps = ["ej_rocketchat", *apps]
        return apps

    def get_third_party_apps(self):
        apps = [*super().get_third_party_apps(), *self.third_party_apps]
        if self.ENVIRONMENT == "local":
            apps = ["debug_toolbar", *apps, "django_extensions"]
        elif self.DEBUG:
            apps = ["debug_toolbar", *apps]
        if self.ENVIRONMENT == "production":
            apps = ["raven.contrib.django.raven_compat", "gunicorn", "anymail", *apps]
        return apps
