from django.conf import settings
from django.core.validators import URLValidator

EJ_WHITELIST_DOMAINS = [
    x.strip() for x in getattr(settings, "EJ_ROCKETCHAT_INTERNAL_DOMAINS", "").split(",")
]


class WhiteListedURLValidator(URLValidator):
    """
    Accepts all validator
    """

    host_re = URLValidator.host_re[:-1] + "|".join(EJ_WHITELIST_DOMAINS) + ")"
