from django.core.management.base import BaseCommand, CommandError

import csv

class Command(BaseCommand):
    help = "import polis data to EJ backend"

    def add_arguments(self, parser):
        parser.add_argument('comments', type=str,
            help='Path to the comments csv file to import')
        parser.add_argument('votes', type=str,
            help='Path to the votes csv file to import')

    def handle(self, *args, **options):
        csv_file_comments_path = options['comments']
        csv_file_votes_path = options['votes']

        with open(csv_file_comments_path, 'r') as csv_file_comments:
            readf = csv.DictReader(csv_file_comments)
            for row in readf:
                xid = row.get('xid')
                comment_id = row.get('comment_id')
                ativo = row.get('ativo')
                created = row.get('created')
                txt = row.get('txt')

        with open(csv_file_votes_path, 'r') as csv_file_votes:
            readf = csv.DictReader(csv_file_votes)
            for row in readf:
                xid = row.get('xid')
                comment_id = row.get('comment_id')
                vote = row.get('vote')
                created = row.get('created')
                print (xid + comment_id + vote + created)
