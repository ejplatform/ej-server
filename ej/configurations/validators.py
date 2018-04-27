from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from . import icons

ICON_LIBS = {
    'material': icons.MATERIAL_ICONS,
    'fa': icons.FONT_AWESOME_ICONS,
}
LIB_NAMES = {
    'material': _('Material icons'),
    'fa': _('Font-awesome icons'),
    'fab': _('Font-awesome brands'),
    'fas': _('Font-awesome solid'),
    'far': _('Font-awesome regular'),
    'fal': _('Font-awesome light'),
}


def validate_icon_name(icon_name, lib='fa'):
    if icon_name not in ICON_LIBS[lib]:
        msg = _(f'{icon_name} is an invalid {LIB_NAMES[lib]} icon!')
        raise ValidationError({'icon_name': msg})
