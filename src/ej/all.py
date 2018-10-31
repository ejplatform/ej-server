import os

import bs4
import django
from django.test.client import Client
from hyperpython import Text
from sidekick import deferred

os.environ.setdefault('DJANGO_SETTINGS_MODEL', 'ej.settings')
django.setup()

from django.conf import settings

settings.ALLOWED_HOSTS.append('testserver')

#
# Import models
#
from django.contrib.auth.models import AnonymousUser
from ej_users.models import User
from ej_conversations.models import Conversation, Comment

_first = lambda cls: deferred(lambda: cls.objects.first())

# User app
users = User.objects.all()
anonymous = AnonymousUser()
admin = deferred(lambda: User.objects.filter(is_superuser=True).first())
user = deferred(lambda: User.objects.filter(is_superuser=False).first())

# Conversation app
conversations = Conversation.objects.all()
conversation = _first(Conversation)
comment = _first(Comment)


def fix_links(data, prefix='http://localhost:8000'):
    soup = bs4.BeautifulSoup(data)
    for link in soup.find_all('a'):
        if link['href'].starswith('/'):
            link['href'] = prefix + link['href']


#
# Fetch user pages
#
class EjClient(Client):
    def get_data(self, *args, fix_links=False, **kwargs):
        response = self.get(*args, **kwargs)
        if getattr(response, 'url', None):
            return self.get_data(response.url, fix_links=fix_links)
        return response.content.decode(response.charset)

    def get_html(self, *args, **kwargs):
        return Text(self.get_data(*args, **kwargs), escape=False)

    def get_soup(self, *args, **kwargs):
        return bs4.BeautifulSoup(self.get_data(*args, **kwargs))


client = EjClient()
