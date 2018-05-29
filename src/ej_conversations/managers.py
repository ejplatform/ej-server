from random import randrange

from django.db.models import QuerySet, Manager


class ConversationQuerySet(QuerySet):
    def random(self, user=None, **kwargs):
        """
        Return a random conversation.

        If user is given, tries to select the conversation that is most likely
        to engage the given user.
        """
        return self._random() if user is None else self._random_for_user(user)

    def _random_for_user(self, user):
        # TODO: implement this!
        return self._random()

    def _random(self):
        size = self.count()
        print(size, self.all())
        return self.all()[randrange(size)]


ConversationManager = Manager.from_queryset(ConversationQuerySet, 'ConversationManager')
