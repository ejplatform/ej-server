from boogie.models import QuerySet, Q
from django.utils import timezone

from ej_conversations.models import Comment


class EndorsementQuerySet(QuerySet):
    def comments_for_user(self, user, comments=None):
        """
        Return a queryset of comments with endorsements for the given user.

        Args:
            user:
                Affected user.
            comments:
                Optional queryset of comments used to filter promotions.
        """
        if not comments:
            comments = Comment.objects.all()
        return comments.filter(Q(endorsements=self.for_user(user)))

    def for_user(self, user):
        """
        Return a queryset of endorsements affecting the given user.
        """
        qs = self.timeframed().filter(is_global=True)
        if not user.is_authenticated:
            return qs
        return qs | self.filter(affected_users__contains=user)

    def timeframed(self):
        """
        Filter only endorsements in the correct timeframe.
        """
        now = timezone.now()
        return self.filter(
            (Q(start__lte=now) | Q(start__isnull=True))
            & (Q(end__gte=now) | Q(end__isnull=True))
        )

    def expired(self):
        """
        Filter expired endorsements.
        """
        now = timezone.now()
        return self.filter(end__lte=now())

    def clean_expired(self):
        """
        Remove the M2M relations for expired comments.
        """
        self.expired().filter(is_global=False)
