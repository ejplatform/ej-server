from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import resolve
from django.utils.translation import ugettext_lazy as _

URL_BLACKLIST = {'', 'me', 'conversations'}


def validate_board_url(url):
    if url in URL_BLACKLIST:
        raise ValidationError(_('Invalid URL.'))
    elif '/' in url:
        raise ValidationError(_('Slug cannot contain a backslash character.'))
    try:
        resolve(f'/{url}/')
    except Http404:
        pass
    else:
        raise ValidationError(_('URL already exists.'))
