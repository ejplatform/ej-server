import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

COLOR_RE = re.compile(r'^\#[0-9A-Fa-f]{6}$')

def validate_color(color):
    if not COLOR_RE.match(color):
        raise ValidationError(_("{color} is a bad color", color=color))
