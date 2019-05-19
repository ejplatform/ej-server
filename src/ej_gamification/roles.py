from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from hyperpython import Blob

trophy_template = get_template('roles/ej/trophy.jinja2')


def profile_trophy(progress):
    return trophy('profile', _('Profile'))


def host_trophy(progress):
    return trophy('host', _('Conversations'))


def commenter_trophy(progress):
    return trophy('commenter', _('Participation'))


def trophy(icon, name):
    """
    Render a trophy
    """
    return Blob(trophy_template.render({
        'icon': icon,
        'name': name,
    }))
