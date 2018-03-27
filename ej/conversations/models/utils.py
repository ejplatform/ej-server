from enum import Enum

from autoslug.settings import slugify as default_slugify
from django.utils.translation import ugettext_lazy as _


def custom_slugify(value):
    return default_slugify(value).lower()


class NUDGE(Enum):
    interval_blocked = {
        'state': 'interval_blocked',
        'message': _('Sorry, you are actually blocked. Please wait be able to post again'),
        'status_code': 429,
        'errors': True,
    }
    global_blocked = {
        'state': 'global_blocked',
        'message': _('Sorry, you cannot post more comments in this conversation'),
        'status_code': 429,
        'errors': True,
    }
    eager = {
        'state': 'eager',
        'message': _('Please, be careful posting too many comments'),
        'status_code': 201,
        'errors': False,
    }
    normal = {
        'state': 'normal',
        'message': _('You can still posting comments'),
        'status_code': 201,
        'errors': False,
    }
