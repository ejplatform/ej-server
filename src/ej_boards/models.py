from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .validators import validate_board_url


class Board(TimeStampedModel):
    """
    A board that contains a list of conversations.
    """
    slug = models.SlugField(
        _('Slug'),
        help_text=(
            'Short text used to identify the board URL (e.g.: "johns-board")'
        ),
        unique=True,
        validators=[validate_board_url],
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boards'
    )
    title = models.CharField(
        _('Title'),
        max_length=50,
    )
    description = models.TextField(
        _('Description'),
        blank=True,
    )

    @property
    def conversations(self):
        return (
            self.board_subscriptions
                .select_related('conversation')
                .values_list('conversation', flat=True)
        )

    class Meta:
        verbose_name = _('Board')
        verbose_name_plural = _('Boards')

    def __str__(self):
        return self.title

    def add_conversation(self, conversation):
        """
        Add conversation to board.
        """
        self.board_subscriptions.add(conversation)


class BoardSubscription(models.Model):
    """
    Subscription of a conversation to a board.
    """
    conversation = models.OneToOneField(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='board_subscriptions',
    )
    board = models.ForeignKey(
        'Board',
        related_name='board_subscriptions',
        on_delete=models.CASCADE,
    )
