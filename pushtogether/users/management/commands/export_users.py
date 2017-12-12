# -*- coding: utf-8 -*-
from __future__ import print_function

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = 'Export users data in a csv file'

    def handle(self, *files, **options):
        with open('users.csv', 'w') as csv:
            csv.write('id, name, username, email, last_login,\n')
            for user in User.objects.all():
                d = '{}, {}, {}, {}, {},\n'.format(str(user.id), str(user.name), str(user.username), str(user.email), str(user.last_login))
                csv.write(d)