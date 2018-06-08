from random import randrange

from django.db.models import Manager

from boogie.models import QuerySet


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
        return self.all()[randrange(size)]


class CommentQuerySet(QuerySet):
    def approved(self):
        return self.filter(status=self.model.STATUS.approved)

    def pending(self):
        return self.filter(status=self.model.STATUS.pending)

    def rejected(self):
        return self.filter(status=self.model.STATUS.rejected)

    def statistics(self):
        return [x.statistics() for x in self]


ConversationManager = Manager.from_queryset(ConversationQuerySet, 'ConversationManager')
CommentManager = Manager.from_queryset(CommentQuerySet, 'CommentManager')
BoogieManager = Manager.from_queryset(QuerySet)
