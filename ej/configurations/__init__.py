from functools import lru_cache

DEFAULT_FRAGMENTS = {}


@lru_cache(256)
def fragment(name, raises=True):
    """
    Return a fragment instance with the given name.
    """
    from .models import Fragment

    try:
        return Fragment.objects.get(name=name)
    except Fragment.DoesNotExist:
        return default_fragment(name, raises)


def default_fragment(name, raises=True):
    from .models import Fragment

    try:
        data = DEFAULT_FRAGMENTS[name]
    except KeyError:
        if raises:
            raise ValueError(f'fragment {name} does not exist')
        else:
            return missing_fragment_error(name)
    return Fragment(name=name, **data)


def missing_fragment_error(name):
    from .models import Fragment

    return Fragment(
        content=f'''
            <h1>
                <strong>You didn't have a "{name}" fragment defined</strong>
                <p>Create a {name}.html</p>
                <p>Use the command loadfragments from manage.py to create new fragments or --force to update</p>
            </h1> 
            '''
    )
