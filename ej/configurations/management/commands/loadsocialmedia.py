import json
from pathlib import Path
from ._load import validate_path
from django.core.management.base import BaseCommand
from ...models import SocialMediaIcon
from django.conf import settings

SITE_ID = getattr(settings, 'SITE_ID', 1)


class Command(BaseCommand):
    help = 'Load JSON file as Social Medias, to be loaded on db and exhibited on the pages'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            type=str,
            help='Path or filename for social media JSON config file',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Override existing social media config.',
        )

    def handle(self, *args, filename, force=False, **options):
        real_handle(filename, force)


def real_handle(filename, force):
    validate_path(filename)

    base = Path(filename)
    data = base.read_text()
    socialmedias = None
    try:
        socialmedias = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("Can't decode JSON file: " + filename)

    current_medias = list(SocialMediaIcon.objects.values_list('social_network'))
    current_medias = list(map(''.join, current_medias))

    new_socialmedias = []
    SocialMediaIcon.objects
    if socialmedias:
        for socialmedia in socialmedias.items():
            if socialmedia[0] not in current_medias or force:
                print(socialmedia)
                new_socialmedias.append(socialmedia)
            else:
                print('Social media Icon exists: %s' % socialmedia[0])

    for socialmedia in new_socialmedias:
        save_media(socialmedia[0], socialmedia[1])


def save_media(social_network, social_network_data):

    social_icon, created = SocialMediaIcon.objects.update_or_create(
        social_network=social_network,
        defaults=social_network_data,
    )

    if(created):
        print('Saved Social Media Icon: %s' % social_icon)
    else:
        print('Updated fragment: %s' % social_icon)

    return social_icon




