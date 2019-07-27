import traceback

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import F

from ej_conversations.models import Conversation, Vote
from ... import get_progress, get_participation

User = get_user_model()


class Command(BaseCommand):
    help = "Update all scores, points and badges for users and conversations in your app"
    log = lambda self, *args, **kwargs: print(*args, **kwargs)

    def handle(self, *args, **options):
        self.update_conversation_points(self.get_conversations())
        self.update_user_points(self.get_users())
        self.update_participation_points(self.get_participations())

    def get_users(self):
        return User.objects.filter(is_active=True)

    def get_conversations(self):
        return Conversation.objects.filter()

    def get_participations(self):
        pairs = set(
            map(
                tuple,
                Vote.objects.annotate(conversation=F("comment__conversation"))
                .values_list("author", "conversation")
                .iterator(),
            )
        )
        users = User.objects.filter(id__in=set(x for x, _ in pairs))
        users = {x.id: x for x in users}
        conversations = Conversation.objects.filter(id__in=set(x for _, x in pairs))
        conversations = {x.id: x for x in conversations}
        for uid, cid in pairs:
            yield users[uid], conversations[cid]

    def update_user_points(self, users):
        return self._update_points(users, "users")

    def update_conversation_points(self, conversations):
        return self._update_points(conversations, "conversations")

    def update_participation_points(self, participations):
        action = lambda x, sync=True: get_participation(*x, sync=sync)
        return self._update_points(participations, "participations", action)

    def _update_points(self, coll, name, action=get_progress):
        self.log(f"Updating {name}".upper())
        n = 0
        for item in coll:
            try:
                action(item, sync=True)
            except Exception as exc:
                print()
                print(f"Error processing: {item}")
                traceback.print_tb(exc.__traceback__)
                print(f"{exc.__class__.__name__}: {exc}")
            n += 1
            self.log(".", end="", flush=True)
            if n % 60 == 0:
                print()
        self.log(f"\n(Updated {n} items)\n")
