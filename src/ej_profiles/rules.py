from boogie import rules
from sidekick import import_later


@rules.register_value('profile.notificationsconfig')
def notificationsconfig(profile):
    """
    Return a notifications config instance for a profile
    """
    notifications_config_class = rules.compute('profile.notificationsconfig_class')
    try:
        return profile.raw_notificationsconfig
    except (notifications_config_class.DoesNotExist):
        return notifications_config_class.objects.create(profile=profile)


@rules.register_value('profile.notificationsconfig_class')
def notificationsconfig_class():
    """
    Return a notifications config class reference
    """
    return import_later('ej_notifications.models:NotificationConfig')
