from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pushtogether.conversations.models import Comment, Conversation, Vote
from django.db.utils import IntegrityError
from django.db import transaction
from datetime import datetime, timezone
from decimal import Decimal

import csv

class Command(BaseCommand):
    help = 'import polis data to EJ backend'

    def add_arguments(self, parser):
        parser.add_argument('comments', type=str,
            help='Path to the comments csv file to import')

    def handle(self, *args, **options):
        csv_file_comments_path = options['comments']
        # csv_file_votes_path = options['votes']

        self.create_comments(csv_file_comments_path)
        # self.create_votes(csv_file_votes_path)

    @transaction.atomic
    def create_comments(self, csv_file_comments_path):
        with open(csv_file_comments_path, 'r') as csv_file_comments:
            readf = csv.DictReader(csv_file_comments, quoting=csv.QUOTE_MINIMAL, quotechar='"', delimiter=',')
            count = 0
            conta_repetidos = 0
            for row in readf:
                comment_id = row.get('comment_id')
                conversation_slug = row.get('conversation_slug')
                xid = row.get('xid')
                if not xid:
                    print('xid for comment_id {}, conversation_slug {} does  not exist'.format(comment_id, conversation_slug))
                    continue
                try:
                    user = get_user_model().objects.get(id=row.get('xid'))
                except get_user_model().DoesNotExist:
                    print('User with xid {} does not exist'.format(xid))
                    continue

                created = datetime.fromtimestamp(Decimal(row.get('created'))/1000, timezone.utc)
                # print('created_original: {}, calculated: {}'.format(row.get('created'), created))
                txt = row.get('txt')
                mod = self.get_moderation_state(int(row.get('mod')))

                try:
                    conversation = Conversation.objects.get(polis_slug=conversation_slug)
                except Conversation.DoesNotExist:
                    print('Conversation for comment_id {}, conversation_slug {} does not exist'.format(comment_id, conversation_slug))

                try:
                    import ipdb

                    if Comment.objects.get(content=txt, polis_id=comment_id):
                        # Now let's take a good look at the comment object. There are objects in the database
                        # inconsistent with Polis database. We have to look at those inconsistencies and only skip
                        # inserting if it is an EXACT COPY.
                        c = Comment.objects.get(content=txt, polis_id=comment_id)
                        if c.author == user and c.approval == mod and c.conversation == conversation and c.created_at == created:
                            print('Comment_id {}, conversation_slug {} already exists'.format(comment_id, conversation_slug))
                            continue
                        else:
                            c.delete()
                            print('Inconsistência encontrada no comment_id {}. Consertando...'.format(comment_id))
                except Comment.DoesNotExist:
                    pass
                except Comment.MultipleObjectsReturned:
                    conta_repetidos = conta_repetidos + 1
                    print('content {}, polis_id {} é repetido'.format(txt, comment_id))
                    continue

                with transaction.atomic():
                    comment = Comment.objects.create(conversation=conversation,
                    author=user, content=txt, polis_id=comment_id, approval=mod)
                    comment.created_at = created
                    comment.save()
                    print('created comment, polis_id:' + comment.polis_id)

                count += 1

            self.stdout.write('Comments created: ' + str(count))
            print('repetidos: {}'.format(conta_repetidos))

    def get_moderation_state(self, mod):
        switcher = {
            0: 'UNMODERATED',
            1: 'APPROVED',
            -1: 'REJECTED',
        }
        return switcher.get(mod, 'nothing')
