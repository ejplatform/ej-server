from django.core.management.base import BaseCommand, CommandError
from pushtogether.users.models import User
from pushtogether.conversations.models import Comment, Conversation, Vote
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction
from datetime import datetime, timezone
from decimal import Decimal
from django.contrib.auth import get_user_model
# from django.db import connection, reset_queries
# from pprint import pprint

import csv

class Command(BaseCommand):
    help = 'import polis votes to EJ backend'

    def add_arguments(self, parser):
        parser.add_argument('votes', type=str,
            help='Path to the votes csv file to import')

    def handle(self, *args, **options):
        csv_file_votes_path = options['votes']

        self.create_votes(csv_file_votes_path)

    @transaction.atomic
    def create_votes(self, csv_file_votes_path):
        with open(csv_file_votes_path, 'r') as csv_file_votes:
            readf = csv.DictReader(csv_file_votes, quoting=csv.QUOTE_MINIMAL, quotechar='"', delimiter=',')
            count = 0
            for row in readf:
                conversation_slug = row.get('conversation_slug')
                xid= row.get('xid')
                vote = self.get_vote_value(row.get('vote'))
                created = datetime.fromtimestamp(Decimal(row.get('created'))/1000, timezone.utc)
                comment_id = row.get('comment_id')
                if not xid:
                    print('xid for comment_id {}, created {} does not exist'.format(comment_id, created))
                    continue
                try:
                    user = get_user_model().objects.get(id=xid)
                except get_user_model().DoesNotExist:
                    print('user with xid {} does not exist'.format(xid))
                    continue

                try:
                    comment = Comment.objects.get(polis_id=comment_id, conversation__polis_slug=conversation_slug)

                except Comment.MultipleObjectsReturned:
                    print('INCONSISTÊNCIA. conversation_slug {}, comment_id {} é repetido'.format(conversation_slug, comment_id))
                    continue
                except Comment.DoesNotExist:
                    print('Conversation_slug {}, comment_id {} não existe'.format(conversation_slug, comment_id))
                    continue

                # try:
                #     print('começou PERF voto')
                #     if Vote.objects.get(comment__polis_id=comment_id, comment__conversation__polis_slug=conversation_slug, author__id=xid):
                #         print('Vote with comment_id {}, author__id {} already exists'.format(comment_id, xid))
                #         continue
                # except Vote.DoesNotExist:
                #     pass
                # except Vote.MultipleObjectsReturned:
                #     print('INCONSISTÊNCIA. comment_id {}, author__id {} tá repetido'.format(comment_id, xid))
                #
                # print('terminou PERF voto')
                try:
                    if Vote.objects.get(comment=comment, author=user):
                        print('Vote with comment_id {}, author {} already exists'.format(comment_id, user))
                        continue
                except Vote.DoesNotExist:
                    pass
                except Vote.MultipleObjectsReturned:
                    print('INCONSISTÊNCIA. comment_id {}, author {} tá repetido'.format(comment_id, user))

                # print('começou PERF CRIAR voto')
                # with transaction.atomic():
                #     vote = Vote.objects.create(comment__polis_id=comment_id, comment__conversation__polis_slug=conversation_slug,
                #                                author_id=xid, value=vote, created_at=created)
                #     vote.created_at = created
                #     vote.save()
                # print('terminou PERF CRIAR voto')

                with transaction.atomic():
                    vote = Vote.objects.create(comment=comment,
                        author=user, value=vote, created_at=created)
                    vote.created_at = created
                    vote.save()
                    print('Vote with comment_id {}, user_id {} created'.format(comment.id, user.id))

                # pprint(connection.queries)
                # reset_queries()

                count += 1
                if count % 1000 == 0:
                    print('Foram {} votos'.format(count))

            self.stdout.write('Votes created: ' + str(count))

    def get_vote_value(self, vote):
        switcher = {
            '0': 0,
            '1': -1,
            '-1': 1,
        }
        return switcher.get(vote)
