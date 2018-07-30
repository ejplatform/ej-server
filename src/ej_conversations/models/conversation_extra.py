from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.models import TaggedItemBase


class FavoriteConversation(models.Model):
    """
    M2M relation from users to conversations.
    """
    conversation = models.ForeignKey(
        'ej_conversations.Conversation',
        on_delete=models.CASCADE,
        related_name='followers',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_conversations',
    )


class ConversationBoard(models.Model):
    """
    A board that contains a list of conversations.
    """
    name = models.CharField(
        _('Board name'),
        max_length=140,
        unique=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boards'
    )


class ConversationTag(TaggedItemBase):
    """
    Add tags to Conversations with real Foreign Keys
    """
    content_object = models.ForeignKey('Conversation', on_delete=models.CASCADE)
