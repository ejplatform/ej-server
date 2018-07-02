import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from ej_users.models import User

try:
    from colortools import COLOR_NAMES

    COLOR_NAMES = dict(COLOR_NAMES)
except ImportError:
    COLOR_NAMES = {}

COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{3,4}(?:[0-9A-Fa-f]{3,4})?$')

# Accepted characters in valid urls
URL_VALID_CHARACTERS = list(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="
)


def validate_color(color):
    if not COLOR_RE.fullmatch(color) and color not in COLOR_NAMES:
        raise ValidationError(_("'{color}' is a bad color value", color=color))


def is_not_empty(text):
    if not text.strip():
        raise ValidationError(_('Field cannot be empty!'))


def validate_board_name(board_name):
    for c in list(board_name):
        if c not in URL_VALID_CHARACTERS:
            raise ValidationError(_("'{char}' is an invalid character!", char=c))
    if User.objects.filter(board_name=board_name):
        raise ValidationError(_("'{board}' already in use!", board=board_name))
