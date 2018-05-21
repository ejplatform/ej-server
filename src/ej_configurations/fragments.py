from functools import lru_cache


#
# Load fragments by name
#
@lru_cache(256)
def fragment(name, raises=True):
    """
    Return a fragment instance with the given name.
    """
    from .models import Fragment

    try:
        return Fragment.objects.get(name=name)
    except Fragment.DoesNotExist:
        return _default_fragment(name, raises)


def _default_fragment(name, raises=True):
    from .models import Fragment

    try:
        data = DEFAULT_FRAGMENTS[name]
    except KeyError:
        if raises:
            raise ValueError(f'fragment {name} does not exist')
        else:
            return _missing_fragment_error(name)
    return Fragment(name=name, **data)


def _missing_fragment_error(name):
    from .models import Fragment

    return Fragment(
        content=MISSING_FRAGMENT.format(name=name),
        format=Fragment.FORMAT_HTML,
    )


#
# Messages
#
MISSING_FRAGMENT = '''
<h1>Missing "{name}" fragment</h1>
<p>Click <a href="/debug/fragments/{name}/" up-modal="main">here</a> to know more</p>
'''


#
# Default messages
#
DEFAULT_FRAGMENTS = {

}
