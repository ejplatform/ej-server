from .models import Fragment, SocialMediaIcon
from .fragments import default_fragment


def get_fragment(name):
    """
    Return a fragment with the given name
    """
    try:
        return Fragment.objects.get(name=name)
    except:
        return default_fragment(name)


def get_social_media_icons():
    """
    Return all social media icons defined
    """
    return list(SocialMediaIcon.objects.all())