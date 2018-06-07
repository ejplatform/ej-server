from sidekick import deferred

from boogie.rules import compute, test_rule
from ej_users.models import User
from ej_conversations.models import Conversation, Comment, Choice

_first = lambda cls: deferred(lambda: cls.objects.first())


# User app
admin = deferred(lambda: User.objects.filter(is_superuser=True).first())
user = deferred(lambda: User.objects.filter(is_superuser=False).first())


# Conversation app
conversation = _first(Conversation)
comment = _first(Comment)
