from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _


class WhiteListedURLValidator(RegexValidator):
    """
    Accepts any semi-valid URL validator ;)
    """

    regex = r"(http|https|ftp|ftps)://.+"
    message = _("Must be a full URL (i.e., do not forget the https:// part).")


def requires_setup_for_blank(password):
    if not password and getattr(settings, "EJ_ROCKETCHAT_ADMIN_PASSWORD"):
        msg = _(
            "Empty passwords are only allowed if EJ_ROCKETCHAT_ADMIN_PASSWORD environment variable is set."
        )
        raise ValidationError(msg)
