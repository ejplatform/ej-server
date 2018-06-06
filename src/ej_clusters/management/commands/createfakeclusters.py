from django.core.management.base import BaseCommand

from ._examples import make_clusters


class Command(BaseCommand):
    help = 'Create synthetic conversation clusters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--silent',
            action='store_true',
            help='Prevents showing debug info',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of clusters',
        )

    def handle(self, *args, silent=False, force=False, **options):
        make_clusters(verbose=not silent, force=force)
