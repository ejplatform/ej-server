from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

if settings.USING_SQLITE:
    import jsonfield
else:
    import django.contrib.postgres.fields as jsonfield

JSONField = jsonfield.JSONField

NOT_GIVEN = object()


def get_related_attr(obj, attr, default=NOT_GIVEN):
    """
    Get attribute, but handle RelatedObjectDoesNotExist exceptions as attribute
    errors.
    """
    try:
        if default is NOT_GIVEN:
            return getattr(obj, attr)
        else:
            return getattr(obj, attr, default)
    except ObjectDoesNotExist:
        if default is NOT_GIVEN:
            raise AttributeError(attr)
        return default
