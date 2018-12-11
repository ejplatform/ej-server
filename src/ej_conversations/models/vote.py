from numbers import Number

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from boogie import models
from boogie.fields import EnumField
from boogie.models import QuerySet
from boogie.rest import rest_api
from .. import Choice
from ..math import imputation

VOTE_ERROR_MESSAGE = _("vote should be one of 'agree', 'disagree' or 'skip', got {value}")
VOTING_ERROR = (lambda value: ValueError(VOTE_ERROR_MESSAGE.format(value=value)))


# ==============================================================================
# QUERYSET

class VoteQuerySet(QuerySet):
    """
    A table of votes.
    """
    votes = (lambda self: self)

    def dataframe(self, *fields, index=None, verbose=False):
        if not fields:
            fields = ('author', 'comment', 'choice')
        return super().dataframe(*fields, index=index, verbose=verbose)

    def votes_table(self, data_imputation=None):
        """
        Return a dataframe with the default representation of vote data in the
        EJ platform.

        Args:
            data_imputation (str):
                Default imputation method for filling missing values. If not
                given, non-filled values become NaN.

                It accepts the following strategies:

                * 'mean': Uses the mean vote value for each comment.
                * 'zero': Uses zero as a filling parameter.
                * numeric value: Uses the given value to fill missing data.

        """
        if data_imputation == 'zero':
            data_imputation = 0

        if isinstance(data_imputation, Number):
            return self.pivot_table('author', 'comment', 'choice', fill_value=data_imputation)
        else:
            data = self.pivot_table('author', 'comment', 'choice')
            return imputation(data, data_imputation)


# ==============================================================================
# MODEL
@rest_api(exclude=['author', 'created'])
class Vote(models.Model):
    """
    A single vote cast for a comment.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='votes',
        on_delete=models.PROTECT,
    )
    comment = models.ForeignKey(
        'Comment',
        related_name='votes',
        on_delete=models.CASCADE,
    )
    choice = EnumField(Choice, _('Choice'), help_text=_('Agree, disagree or skip'))
    created = models.DateTimeField(_('Created at'), auto_now_add=True)
    objects = VoteQuerySet.as_manager()

    class Meta:
        unique_together = ('author', 'comment')
        ordering = ['id']

    def __str__(self):
        comment = truncate(self.comment.content, 40)
        return f'{self.author} - {self.choice.name} ({comment})'

    def clean(self, *args, **kwargs):
        if self.comment.is_pending:
            msg = _('non-moderated comments cannot receive votes')
            raise ValidationError(msg)


# ==============================================================================
# UTILITY FUNCTIONS

VOTE_NAMES = {Choice.AGREE: 'agree', Choice.DISAGREE: 'disagree', Choice.SKIP: 'skip'}
VOTE_VALUES = {v: k for k, v in VOTE_NAMES.items()}


def normalize_choice(value):
    """
    Normalize numeric and string values to the correct vote value that
    should be stored in the database.
    """
    if value in VOTE_NAMES:
        return value
    try:
        return VOTE_VALUES[value]
    except KeyError:
        raise VOTING_ERROR(value)


def truncate(st, size):
    if len(st) > size - 2:
        return st[:size - 3] + '...'
    return st
