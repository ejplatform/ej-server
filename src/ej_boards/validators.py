from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

URL_BLACKLIST = {'', 'me', 'conversations'}


def validate_board_slug(slug):
    if slug in URL_BLACKLIST:
        raise ValidationError(_('Invalid slug.'))
    elif '/' in slug:
        raise ValidationError(_('Slug cannot contain a backslash character.'))

def validate_sub_domain(sub_domain):
    """
    Validates if sub_domain is a subdomain from the
    application domain.
    """
    from django.conf import settings
    import re
    domain = settings.SESSION_COOKIE_DOMAIN
    if(not(re.match("^.*"+ domain, sub_domain))):
        raise ValidationError( _('This field must be a subdomain of %s' % str(domain[1:])))
