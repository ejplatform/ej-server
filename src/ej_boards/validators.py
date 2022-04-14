from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

URL_BLACKLIST = {"", "me", "conversations"}


def validate_board_slug(slug):
    if slug in URL_BLACKLIST:
        raise ValidationError(_("Invalid slug."))
    elif "/" in slug:
        raise ValidationError(_("Slug cannot contain a backslash character."))
