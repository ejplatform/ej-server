from boogie import rules
from sidekick import import_later


@rules.register_value('auth.profile')
def profile(user):
    """
    Return a profile instance for user.
    """
    profile_class = rules.compute('auth.profile_class')
    try:
        return user.raw_profile
    except (profile_class.DoesNotExist, user._meta.model.raw_profile.RelatedObjectDoesNotExist):
        return profile_class.objects.create(user=user)


@rules.register_value('auth.profile_class')
def profile_class():
    """
    Return a profile instance for user.
    """
    return import_later('ej_profiles.models:Profile')
