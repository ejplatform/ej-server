from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext as _

EJ_WHITELIST_DOMAINS = [
    x.strip() for x in getattr(settings, "EJ_ROCKETCHAT_INTERNAL_DOMAINS", "").split(",")
]


class WhiteListedURLValidator(URLValidator):
    """
    Accepts all validator
    """

    host_re = URLValidator.host_re[:-1] + "|".join(EJ_WHITELIST_DOMAINS) + ")"


def requires_setup_for_blank(password):
    if not password and getattr(settings, "EJ_ROCKETCHAT_ADMIN_PASSWORD"):
        msg = _(
            "Empty passwords are only allowed if EJ_ROCKETCHAT_ADMIN_PASSWORD environment variable is set."
        )
        raise ValidationError(msg)
