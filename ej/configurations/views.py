from .models import SocialMediaIcon


def get_social_media_icons():
    """
    Return all social media icons defined
    """
    return list(SocialMediaIcon.objects.all())
