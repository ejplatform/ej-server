from functools import singledispatch

from django.db.models import Model, QuerySet


@singledispatch
def title(obj):
    """
    Return title associated with object.
    """
    try:
        return obj.title
    except AttributeError:
        cls_name = type(obj).__name__
        raise TypeError(f'cannot determine title for object: {cls_name}')


@title.register(Model)
def _(model):
    try:
        return model.title
    except AttributeError:
        return model._meta.verbose_name


@title.register(QuerySet)
def _(qs):
    return qs.model._meta.verbose_name_plural
