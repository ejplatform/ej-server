import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from ._load import validate_path
from ...models import SocialMediaIcon

SITE_ID = getattr(settings, 'SITE_ID', 1)
icon_db = SocialMediaIcon.objects


class Command(BaseCommand):
    help = 'Load JSON file as social media icons exhibited on page navigational elements'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path or filename for social media JSON config file',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Override existing social media config.',
        )

    def handle(self, *args, path, force=False, **options):
        if not path:
            path = Path(path) / 'social-icons.json'
        real_handle(path, force)


def real_handle(filename, force):
    validate_path(filename)

    data = Path(filename).read_text()
    try:
        icon_data = json.loads(data)
    except json.decoder.JSONDecodeError:
        raise SystemExit("Can't decode JSON file: " + filename)

    installed = set(icon_db.values_list('social_network', flat=True))

    icons = []
    for network in icon_data:
        if network not in installed or force:
            icons.append(save_icon(network, icon_data[network]))
        else:
            print('Social media Icon exists: %s' % network)
    return icons


def save_icon(social_network, data):
    with transaction.atomic():
        social_icon, created = icon_db.update_or_create(
            social_network=social_network,
            defaults=data,
        )
        social_icon.full_clean()
        social_icon.save()
    print('Saved:' if created else 'Updated:', social_icon)
    return social_icon
