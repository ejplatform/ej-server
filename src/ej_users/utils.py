from secrets import token_urlsafe

from boogie.utils import random_name as _random_name


def random_name():
    # This function stays here to be picklable from a location we can control.
    # In the future we may want to add other sources of random names and
    # avoid an unnecessary migration because the location of the function
    # changed.
    return _random_name()


def token_factory():
    return token_urlsafe(30)
