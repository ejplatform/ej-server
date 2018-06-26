from django.conf import settings
from django.urls import resolve, Resolver404

from boogie import rules
from sidekick import import_later


USERNAMES_BLACKLIST = {
    # Common 'bad' usernames
    'me', '', 'user',

    # Additional usernames from settings
    *getattr(settings, 'FORBIDDEN_USERNAMES', ()),
}

# accepted characters in valid urls
URL_VALID_CHARACTERS = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="
)

@rules.register_rule('auth.valid_username')
def is_valid_username(username):
    if username in USERNAMES_BLACKLIST:
        return False
    try:
        resolve(f'/{username}/')
        return False
    except Resolver404:
        return True


@rules.register_rule('auth.valid_board_name')
def is_valid_board_name(board_name):
    for c in list(board_name):
        if c not in URL_VALID_CHARACTERS:
            return False
    try:
        resolve(f'/{board_name}/')
        return False
    except Resolver404:
        return True


@rules.register_value('auth.profile')
def profile(user):
    """
    Return a profile instance for user.
    """
    profile_class = rules.compute('auth.profile_class')
    try:
        return user.raw_profile
    except profile_class.DoesNotExist:
        return profile_class.objects.create(user=user)


@rules.register_value('auth.profile_class')
def profile_class():
    """
    Return a profile instance for user.
    """
    return import_later('ej_profiles.models:Profile')
