from django.core.management.base import BaseCommand

from ._examples import make_examples


class Command(BaseCommand):
    help = "Create synthetic conversation examples"

    def add_arguments(self, parser):
        parser.add_argument(
            "--silent", action="store_true", help="Prevents showing debug info"
        )

    def handle(self, *args, silent=False, **options):
        make_examples(verbose=not silent)
