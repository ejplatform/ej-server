from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from ej.utils.url import SafeUrl
from ej_conversations.models import Conversation, ConversationTag
from .validators import *


class Board(TimeStampedModel):
    """
    A board that contains a list of conversations.
    """
    slug = models.SlugField(
        _('Slug'),
        unique=True,
        validators=[validate_board_slug],
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

    PALLET_CHOICES = (
        ('Blue', 'Blue'),
      ('Grey', 'Grey'),
      ('Pink', 'Pink'),
      ('Green', 'Green'),
      ('Orange', 'Orange'),
      ('Purple', 'Purple'),
    )

    palette = models.CharField(_('Palette'),
                               max_length=10,
                               choices=PALLET_CHOICES,
                               default='Blue')

    image = models.ImageField(_('Image'),
                              blank=True,
                              null=True)

    custom_domain = models.CharField(
      _('Custom Domain'),
      blank= True,
      max_length=50,
      unique=True,
      validators=[
        RegexValidator(
          regex='\w{3}.?[a-z]+\.[a-z]+',
          message='Domínio invalido'
        ),
        validate_custom_domain
      ]
    )


    @property
    def conversations(self):
        return Conversation.objects.filter(board_subscriptions__board=self)

    @property
    def tags(self):
        return ConversationTag.objects.all()

    class Meta:
        verbose_name = _('Board')
        verbose_name_plural = _('Boards')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = slugify(self.slug)
        super().save(*args, **kwargs)

    def clean(self):
        try:
            board = Board.objects.get(slug=self.slug)
            if board.slug == self.slug and board.id != self.id:
                raise ValidationError(_('Slug already exists.'))
        except Board.DoesNotExist:
            pass

    def get_absolute_url(self):
        return f'/{self.slug}/'

    def add_conversation(self, conversation):
        """
        Add conversation to board.
        """
        self.board_subscriptions.get_or_create(conversation=conversation)

    def has_conversation(self, conversation):
        """
        Return True if conversation is present in board.
        """
        return bool(self.board_subscriptions.filter(conversation=conversation))

    def get_url(self, which, **kwargs):
        kwargs['board'] = self
        return SafeUrl(which, **kwargs)

    @property
    def css_palette(self):
        return self.palette.lower() + 'Palette'

    @staticmethod
    def get_default_css_palette():
        return 'bluePalette'


    @staticmethod
    def with_custom_domain(domain):
      try:
        board = Board.objects.get(custom_domain=domain).slug;
        return [board, True]
      except:
        return [None, False]

    @property
    def custom_domain_with_scheme(self):
        custom_domain = 'https://' + self.custom_domain
        return '/'.join([custom_domain, self.slug, 'conversations'])

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
