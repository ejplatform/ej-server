import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .icons import LIB_ICONS

FONT_AWESOME_NAME_RE = re.compile(r'fa[bsrl]? fa-[a-z]+(?:-[a-z]+)*')
LIB_NAMES = {
    'fa': _('Font-awesome icons'),
    'fab': _('Font-awesome brands'),
    'fas': _('Font-awesome solid'),
    'far': _('Font-awesome regular'),
    'fal': _('Font-awesome light'),
}


def validate_icon_name(icon_name):
    if not FONT_AWESOME_NAME_RE.fullmatch(icon_name):
        raise ValidationError(_(
            'Invalid font awesome icon name. Please use the full format like '
            'in "fab fa-facebook-f"'
        ))

    lib, _sep, full_name = icon_name.partition(' ')
    _fa, _sep, name = full_name.partition('-')

    if name not in LIB_ICONS[lib]:
        msg = _(f'{icon_name} is an invalid {LIB_NAMES[lib]} icon!')
        raise ValidationError(msg)
