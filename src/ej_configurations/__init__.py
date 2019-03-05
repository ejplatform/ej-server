default_app_config = 'ej_configurations.apps.EjConfigurationsConfig'

from .fragments import fragment  # noqa: F401


#TODO: remove this function once the landing page is stable.
def social_icons():
    """
    Return all social media icons defined
    """
    from .models import SocialMediaIcon

    return list(SocialMediaIcon.objects.all())
