import contextlib

import sidekick as sk
from django.db import transaction
from django.http import Http404


@contextlib.contextmanager
def use_transaction(which=None, **kwargs):
    """
    Context manager that puts the block inside a transaction of the specified
    kind.
    """
    kinds = {'atomic', 'commit', 'rollback'}

    if which in kinds:
        kwargs[which] = True
    elif which is not None:
        raise ValueError(f'invalid operation: {which}')

    methods, args = sk.split_by(kinds.__contains__, kwargs)
    methods = [getattr(transaction, k) for k in methods if kwargs[k]]
    kwargs = {k: kwargs[k] for k in args}

    if not methods:
        yield None
    else:
        method, *rest = methods
        rest = {k: True for k in rest}
        with use_transaction(**rest, **kwargs), method(**kwargs) as handler:
            yield handler


def check_stereotype(stereotype, user):
    if stereotype.owner != user:
        raise Http404
    return stereotype
