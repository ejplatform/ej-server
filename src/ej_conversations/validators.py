import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

try:
    from colortools import COLOR_NAMES

    COLOR_NAMES = dict(COLOR_NAMES)
except ImportError:
    COLOR_NAMES = {}

COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{3,4}(?:[0-9A-Fa-f]{3,4})?$')


def validate_color(color):
    if not COLOR_RE.fullmatch(color) and color not in COLOR_NAMES:
        raise ValidationError(_("'{color}' is a bad color value", color=color))


def is_not_empty(text):
    if not text.strip():
        raise ValidationError(_('Field cannot be empty!'))