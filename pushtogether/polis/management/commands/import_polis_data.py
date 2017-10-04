from django.core.management.base import BaseCommand, CommandError

import csv

class Command(BaseCommand):
    help = "import polis data to EJ backend"

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str,
            help='Path to the csv file to import', required=True)
        parser.add_argument('-t', '--type', type=str,
            help='Csv file type (comments or votes)', required=True)

    def handle(self, *args, **options):
        csv_file_path = options['file']
        csv_file_type = options['type']

        if csv_file_type != 'comments' and csv_file_type != 'votes':
            raise CommandError('Argument --type must be \'comments\' or \'votes\'')

        with open(csv_file_path, 'r') as csvfile:
            readf = csv.DictReader(csvfile)
            for row in readf:
                if csv_file_type == 'comments':
                    xid = row.get('xid')
                    comment_id = row.get('comment_id')
                    ativo = row.get('ativo')
                    created = row.get('created')
                    txt = row.get('txt')
                    #TODO create comment and save

                elif csv_file_type == 'votes':
                    xid = row.get('xid')
                    commnet_id = row.get('comment_id')
                    vote = row.get('vote')
                    created = row.get('created')
                    #TODO create vote and save
