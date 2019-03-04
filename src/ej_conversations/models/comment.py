from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel, StatusModel
from sidekick import lazy

from boogie import models
from boogie.rest import rest_api
from .comment_queryset import CommentQuerySet, log
from .vote import Vote, normalize_choice
from ..enums import Choice, RejectionReason
from ..utils import votes_counter
from ..validators import is_not_empty


# noinspection PyUnresolvedReferences
@rest_api(['content', 'author', 'status', 'created', 'rejection_reason'])
class Comment(StatusModel, TimeStampedModel):
    """
    A comment on a conversation.
    """

    STATUS = Choices(
        ('pending', _('awaiting moderation')),
        ('approved', _('approved')),
        ('rejected', _('rejected')),
    )
    STATUS_MAP = {
        'pending': STATUS.pending,
        'approved': STATUS.approved,
        'rejected': STATUS.rejected,
    }
    REJECTION_REASON = Choices(
        ('incomplete_text', _('Incomplete or incomprehensible text')),
        ('off_topic', _('Off-topic')),
        ('offensive_language', _('Offensive content or language')),
        ('duplicated_comment', _('Duplicated content')),
        ('against_terms_of_service', _('Violates terms of service of the platform')),
    )
    conversation = models.ForeignKey(
        'Conversation',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    content = models.TextField(
        _('Content'),
        max_length=252,
        validators=[MinLengthValidator(2), is_not_empty],
        help_text=_('Body of text for the comment'),
    )
    rejection_reason_option = models.EnumField(
        RejectionReason,
        _('Rejection reason'),
        null=True, blank=True,
    )
    rejection_reason = models.TextField(
        _('Rejection reason (free-form)'),
        blank=True,
        help_text=_(
            'You must provide a reason to reject a comment. Users will receive '
            'this feedback.'
        ),
    )
    is_promoted = models.BooleanField(
        _('Promoted comment?'),
        default=False,
        help_text=_(
            'Promoted comments are prioritized when selecting random comments'
            'to users.'
        ),
    )
    is_approved = property(lambda self: self.status == self.STATUS.approved)
    is_pending = property(lambda self: self.status == self.STATUS.pending)
    is_rejected = property(lambda self: self.status == self.STATUS.rejected)
    has_rejection_explanation = property(lambda self: bool(self.rejection_reason == ''
                                                           or self.rejection_reason_option is None))

    @lazy
    def missing_votes(self):
        return self.conversation.users.count() - self.total_votes

    # Statistics
    @property
    def agree_count(self):
        try:
            return self.annotation_agree_count
        except AttributeError:
            return votes_counter(self, choice=Choice.AGREE)

    @property
    def skip_count(self):
        try:
            return self.annotation_skip_count
        except AttributeError:
            return votes_counter(self, choice=Choice.SKIP)

    @property
    def disagree_count(self):
        try:
            return self.annotation_disagree_count
        except AttributeError:
            return votes_counter(self, choice=Choice.DISAGREE)

    @property
    def total_votes(self):
        try:
            return self.annotation_total_votes
        except AttributeError:
            return self.agree_count + self.disagree_count + self.skip_count

    @property
    def rejection_reason_display(self):
        if self.status == self.STATUS.approved:
            return _('Comment is approved')
        elif self.status == self.STATUS.pending:
            return _('Comment is pending moderation')
        elif self.rejection_reason:
            return rejection_reason
        elif self.rejection_reason_option is not None:
            return self.rejection_reason_option.description
        else:
            raise AssertionError

    objects = CommentQuerySet.as_manager()

    class Meta:
        unique_together = ('conversation', 'content')

    def __str__(self):
        return self.content

    def clean(self):
        super().clean()
        print(self, self.status, self.rejection_reason, self.rejection_reason_option, self.has_rejection_explanation)
        if self.status == self.STATUS.rejected and not self.has_rejection_explanation:
            msg = _('Must give a reason to reject a comment')
            raise ValidationError({'rejection_reason': msg})

    def vote(self, author, choice, commit=True):
        """
        Cast a vote for the current comment. Vote must be one of 'agree', 'skip'
        or 'disagree'.

        >>> comment.vote(user, 'agree')                         # doctest: +SKIP
        """
        choice = normalize_choice(choice)
        log.debug(f'Vote: {author} - {choice}')
        vote = Vote(author=author, comment=self, choice=choice)
        vote.full_clean()
        if commit:
            vote.save()
        return vote

    def statistics(self, ratios=False):
        """
        Return full voting statistics for comment.

        Args:
            ratios (bool):
                If True, also include 'agree_ratio', 'disagree_ratio', etc
                fields each original value. Ratios count the percentage of
                votes in each category.

        >>> comment.statistics()                            # doctest: +SKIP
        {
            'agree': 42,
            'disagree': 10,
            'skip': 25,
            'total': 67,
            'missing': 102,
        }
        """

        stats = {
            'agree': self.agree_count,
            'disagree': self.disagree_count,
            'skip': self.skip_count,
            'total': self.total_votes,
            'missing': self.missing_votes
        }

        if ratios:
            e = 1e-50  # prevents ZeroDivisionErrors
            stats.update(
                agree_ratio=self.agree_count / (self.total_votes + e),
                disagree_ratio=self.disagree_count / (self.total_votes + e),
                skip_ratio=self.skip_count / (self.total_votes + e),
                missing_ratio=self.missing_votes / (self.missing_votes + self.total_votes + e),
            )
        return stats
