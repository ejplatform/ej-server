from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from hyperpython.components.fa_icons import COLLECTIONS


def validate_icon_name(icon_name):
    if icon_name not in COLLECTIONS:
        raise ValidationError(_(
            'Invalid font awesome icon name. Please use the short format (i.e., '
            '"facebook-f" instead of "fab fa-facebook-f"'
        ))
