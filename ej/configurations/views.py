from .models import Fragment
from .fragments import DEFAULT_FRAGMENTS


def get_fragment(name):
    """
    Return a fragment with the given name
    """
    custom_fragment = Fragment.objects.filter(name=name)
    if custom_fragment:
        return custom_fragment
    else:
        try:
            return DEFAULT_FRAGMENTS[name]
        except KeyError:
            raise ValueError(f'Invalid fragment name "{name}"!')    