import os

import bs4
import django
from django.test.client import Client
from hyperpython import Text
from sidekick import deferred, import_later

pd = import_later('pandas')
np = import_later('numpy')
plt = import_later('matplotlib.pyplot')

os.environ.setdefault('DJANGO_SETTINGS_MODEL', 'ej.settings')
django.setup()

#
# Django imports
#
from boogie.models import F, Q
from django.conf import settings  # noqa: E402
from django.contrib.auth.models import AnonymousUser  # noqa: E402
from ej_users.models import User  # noqa: E402
from ej_conversations.models import Conversation, Comment, Vote, FavoriteConversation, ConversationTag  # noqa: E402
from ej_clusters.models import Clusterization, Stereotype, Cluster, ClusterStatus, StereotypeVote  # noqa: E402

_export = {F, Q}
_enums = {ClusterStatus}

#
# Create examples
#
settings.ALLOWED_HOSTS.append('testserver')

_first = lambda obj: deferred(lambda: obj.first())


def extract(obj):
    return obj._obj__


# User app
users = User.objects
anonymous = AnonymousUser()
admin = deferred(lambda: users.filter(is_superuser=True).first())
user = deferred(lambda: users.filter(is_superuser=False).first())

# Conversation app
conversations = Conversation.objects
conversation = _first(conversations)
comment = _first(Comment)
votes = Vote.objects
favorite_conversations = FavoriteConversation.objects
conversation_tags = ConversationTag.objects

# Clusterizations app
clusterizations = Clusterization.objects
clusterization = _first(clusterizations)
stereotypes = Stereotype.objects
stereotype = _first(stereotypes)
clusters = Cluster.objects
stereotype_votes = StereotypeVote.objects


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
