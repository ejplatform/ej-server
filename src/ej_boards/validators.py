from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

URL_BLACKLIST = {'', 'me', 'conversations'}


def validate_board_slug(slug):
    if slug in URL_BLACKLIST:
        raise ValidationError(_('Invalid slug.'))
    elif '/' in slug:
        raise ValidationError(_('Slug cannot contain a backslash character.'))

def validate_custom_domain(custom_domain):
    """
    Validates if custom_domain is a sub domain from the 
    application domain.
    """
    from django.conf import settings
    import re
    valid_domains = settings.ALLOWED_HOSTS
    valid_domain = False
    for domain in valid_domains:
        domain_without_subdomain_rule = domain[1:]
        if(re.match('^.*\.\.?'+ domain_without_subdomain_rule, custom_domain)):
            valid_domain = True
            break
    if (not valid_domain):
        raise ValidationError( _('custom_domain must be a sobdomain of %s' % str(valid_domains)))
