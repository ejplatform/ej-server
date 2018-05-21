from django.apps import AppConfig
from django.conf import settings


class UsersConfig(AppConfig):
    name = 'ej_users'
    verbose_name = "Users"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        if 'actstream' in settings.INSTALLED_APPS:
            from actstream import registry
            registry.register(self.get_model('User'))
