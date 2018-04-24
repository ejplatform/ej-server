from .models import Fragment
from .fragments import DEFAULT_FRAGMENTS


def get_fragment(name):
    """
    Return a fragment with the given name
    """
    try:
        return DEFAULT_FRAGMENTS[name]
    except KeyError:
        custom_fragment = Fragment.objects.filter(name=name)
        if custom_fragment:
            return custom_fragment
        else:
            raise ValueError(f'Invalid fragment name "{name}"!')    