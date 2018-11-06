from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ej_conversations.models import Conversation
from ._examples import make_clusters
from ...factories import cluster_votes
User = get_user_model()


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
        if force:
            Conversation.objects.filter(title='Economy').delete()
        make_clusters(verbose=not silent)

        conversation = Conversation.objects.get(title='Economy')
        cluster_votes(conversation, User.objects.all())
