from logging import getLogger

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

log = getLogger('ej')


class RCConfigManager(models.Manager):
    """
    Manager class for RCConfig objects.
    """

    def default_config(self, raises=True):
        """
        Return the default config instance.

        If raises=False, return None instead of raising an ImproperlyConfigured
        exception for cases in which the default config does not exist.
        """
        try:
            return self.get(is_active=True)
        except self.model.DoesNotExist:
            if has_settings(settings):
                url = settings.EJ_ROCKETCHAT_URL
                token = settings.EJ_ROCKETCHAT_AUTH_TOKEN
                user_id = settings.EJ_ROCKETCHAT_USER_IR
                return self.model(url=url, admin_id=user_id, admin_token=token)

            log.error('RocketChat settings were not configured.')
            if raises:
                raise ImproperlyConfigured(
                    'Rocketchat integration was not correctly configured\n'
                    '\n'
                    'Please go to /rocketchat/config/ as an administrator to '
                    'configure the RocketChat integration.'
                )
            return None


def has_settings(settings):
    """
    Return True if all settings are defined.
    """
    return settings.EJ_ROCKETCHAT_URL \
           and settings.EJ_ROCKETCHAT_AUTH_TOKEN \
           and settings.EJ_ROCKETCHAT_USER_IR
