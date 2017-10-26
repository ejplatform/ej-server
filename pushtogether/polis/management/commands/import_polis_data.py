from django.core.management.base import BaseCommand, CommandError
from pushtogether.users.models import User
from pushtogether.conversations.models import Comment, Conversation, Vote
from django.db.utils import IntegrityError
from django.db import transaction

import csv

class Command(BaseCommand):
    help = 'import polis data to EJ backend'

    def add_arguments(self, parser):
        parser.add_argument('comments', type=str,
            help='Path to the comments csv file to import')
        parser.add_argument('votes', type=str,
            help='Path to the votes csv file to import')

    def handle(self, *args, **options):
        csv_file_comments_path = options['comments']
        csv_file_votes_path = options['votes']

        self.create_comments(csv_file_comments_path)
        self.create_votes(csv_file_votes_path)

    @transaction.atomic
    def create_comments(self, csv_file_comments_path):
        with open(csv_file_comments_path, 'r') as csv_file_comments:
            readf = csv.DictReader(csv_file_comments)
            count = 0
            for row in readf:
                xid = row.get('xid')
                comment_id = row.get('comment_id')
                created = row.get('created')
                txt = row.get('txt')
                mod = self.get_moderation_state(int(row.get('mod')))
                user = self.find_user_by_xid(xid)
                if not user:
                    continue

                #TODO get conversation created
                conversation = Conversation.objects.get(id=1)

                try:
                    with transaction.atomic():
                        comment = Comment.objects.create(conversation=conversation,
                        author=user, content=txt, polis_id=comment_id, created_at=created, approval=mod)
                    print('created comment, polis_id:' + comment.polis_id)
                except IntegrityError as e:
                    comment = Comment.objects.get(polis_id=comment_id)
                    print('found comment, polis_id: ' + comment.polis_id)
                    continue

                count += 1

            self.stdout.write('Comments created: ' + str(count))

    @transaction.atomic
    def create_votes(self, csv_file_votes_path):
        with open(csv_file_votes_path, 'r') as csv_file_votes:
            readf = csv.DictReader(csv_file_votes)
            count = 0
            for row in readf:
                xid = row.get('xid')
                comment_id = row.get('comment_id')
                vote = row.get('vote')
                created = row.get('created')
                vote_id = row.get('vote_id')
                user = self.find_user_by_xid(xid)
                if not user:
                    continue

                try:
                    comment = Comment.objects.get(polis_id=comment_id)
                except  Comment.DoesNotExist:
                    self.stdout.write('comment does not exist, polis_id: ' + comment_id)
                    continue

                try:
                    with transaction.atomic():
                        vote = Vote.objects.create(comment=comment,
                        author=user, value=vote, polis_id=vote_id, created_at=created)
                    print('created vote, polis_id:' + str(vote.polis_id))
                except IntegrityError as e:
                    vote = Vote.objects.get(polis_id=1)
                    print('found vote, polis_id: ' + str(vote.polis_id))
                    continue

                count += 1

            self.stdout.write('Votes created: ' + str(count))

    def find_user_by_xid(self, xid):
        if xid:
            try:
                user = User.objects.get(id=xid)
            except  User.DoesNotExist:
                self.stdout.write('user does not exist')
                user = None
        else:
            #TODO get user with admin id
            user = User.objects.get(id=1)
        return user

    def get_moderation_state(self, mod):
        switcher = {
            0: 'UNMODERATED',
            1: 'APPROVED',
            -1: 'REJECTED',
        }
        return switcher.get(mod, 'nothing')
