import picklefield
from django.contrib.auth import get_user_model
from django.db import models

try:
    import autoslug
except ImportError:
    from django import urls
    import sys

    # Restore old Django API if Autoslugfield import fail for Django 2.0 and
    # older versions of the package.
    sys.modules['django.core.urlresolvers'] = urls
    import autoslug

AutoSlugField = autoslug.AutoSlugField
NumpyArrayField = picklefield.PickledObjectField


def UserRef(**kwargs):
    kwargs.setdefault('on_delete', models.CASCADE)
    return models.ForeignKey(get_user_model(), **kwargs)


def ConversationRef(**kwargs):
    kwargs.setdefault('on_delete', models.CASCADE)
    return models.ForeignKey('ej_conversations.Conversation', **kwargs)


def CommentRef(**kwargs):
    kwargs.setdefault('on_delete', models.CASCADE)
    return models.ForeignKey('ej_conversations.Comment', **kwargs)
