import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

try:
    from colortools import COLOR_NAMES

    COLOR_NAMES = dict(COLOR_NAMES)
except ImportError:
    COLOR_NAMES = {}

COLOR_RE = re.compile(r'^\#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$')


def validate_color(color):
    if not COLOR_RE.fullmatch(color) and color not in COLOR_NAMES:
        raise ValidationError(_("{color} is a bad color", color=color))
