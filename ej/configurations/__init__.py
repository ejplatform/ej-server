from .fragments import fragment


def social_icons():
    """
    Return all social media icons defined
    """
    from .models import SocialMediaIcon

    return list(SocialMediaIcon.objects.all())
