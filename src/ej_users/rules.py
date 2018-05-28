from django.conf import settings
from django.urls import resolve, Resolver404

from boogie import rules

USERNAMES_BLACKLIST = {'me', '', *getattr(settings, 'FORBIDDEN_USERNAMES', ())}


@rules.register_rule('ej_users.valid_username')
def is_valid_username(username):
    if username in USERNAMES_BLACKLIST:
        return False
    try:
        view = resolve(f'/{username}/')
        print(view)
        return False
    except Resolver404:
        return True
