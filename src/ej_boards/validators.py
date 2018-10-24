from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


URL_BLACKLIST = {'', 'me', 'conversations'}


def validate_board_slug(slug):
    if slug in URL_BLACKLIST:
        raise ValidationError(_('Invalid slug.'))
    elif '/' in slug:
        raise ValidationError(_('Slug cannot contain a backslash character.'))
