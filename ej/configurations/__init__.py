from functools import lru_cache

from .fragments import DEFAULT_FRAGMENTS


@lru_cache(256)
def fragment(name):
    """
    Return a fragment instance with the given name.
    """
    from .models import Fragment

    try:
        return Fragment.objects.get(name=name)
    except Fragment.DoesNotExist:
        return default_fragment(name)


def default_fragment(name):
    from .models import Fragment

    try:
        data = DEFAULT_FRAGMENTS[name]
    except KeyError:
        raise ValueError(f'fragment {name} does not exist')
    return Fragment(name=name, **data)
