from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .category import log
from .vote import Vote


class Comment(models.Model):
    """
    A comment on a conversation.
    """

    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    PENDING = 'UNMODERATED'  # FIXME: should be NOT_MODERATED or PENDING ;)

    APPROVAL_CHOICES = (
        (APPROVED, _('approved')),
        (REJECTED, _('rejected')),
        (PENDING, _('awaiting moderation')),
    )
    conversation = models.ForeignKey(
        'Conversation',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.PROTECT,
    )
    content = models.TextField(
        _('Content'),
        blank=False,
        validators=[MaxLengthValidator(140)],
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
    )
    approval = models.CharField(
        _('Approval'),
        max_length=32,
        choices=APPROVAL_CHOICES,
        default=PENDING,
    )
    rejection_reason = models.TextField(
        _('Rejection reason'),
        null=True, blank=True,
    )

    def __str__(self):
        return self.content

    @property
    def agree_votes(self):
        return self.votes.filter(value=Vote.AGREE).count()

    @property
    def disagree_votes(self):
        return self.votes.filter(value=Vote.DISAGREE).count()

    @property
    def pass_votes(self):
        return self.votes.filter(value=Vote.PASS).count()

    @property
    def total_votes(self):
        return self.votes.count()

    def vote(self, user, vote, commit=True):
        """
        Cast a user vote for the given comment.
        """
        log.debug(f'Vote: {user} - {vote}')
        make_vote = Vote.objects.create if commit else Vote
        return make_vote(author=user, comment=self, value=vote)
