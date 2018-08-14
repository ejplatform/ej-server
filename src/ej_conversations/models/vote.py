from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from boogie.fields import IntEnum, EnumField
from boogie.rest import rest_api


#
# Constants and enums
#
class Choice(IntEnum):
    SKIP = 0, _('Skip')
    AGREE = 1, _('Agree')
    DISAGREE = -1, _('Disagree')


VOTE_NAMES = {
    Choice.AGREE: 'agree',
    Choice.DISAGREE: 'disagree',
    Choice.SKIP: 'skip',
}
VOTE_VALUES = {v: k for k, v in VOTE_NAMES.items()}
VOTING_ERROR = (lambda value: ValueError(
    f"vote should be one of 'agree', 'disagree' or 'skip', got {value}")
)


#
# Model class
#
@rest_api(exclude=['created'])
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
