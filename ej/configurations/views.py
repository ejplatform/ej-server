from .models import Fragment
from .fragments import default_fragment


def get_fragment(name):
    """
    Return a fragment with the given name
    """
    try:
        return Fragment.objects.get(name=name)
    except:
        return default_fragment(name)
