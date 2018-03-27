import logging

from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import custom_slugify
from ...utils.fields import JSONField

log = logging.getLogger('conversations')


class Category(models.Model):
    """
    Base category that a conversation belongs to.

    Declares category name and stores some metadata.
    """
    # TODO: document customizations JSON field

    name = models.CharField(
        _('Name'),
        max_length=255,
        unique=True,
        help_text=_('Unique category name. Hint: list of categories is public.'),
    )
    slug = AutoSlugField(
        null=True, default=None,
        unique=True,
        populate_from='name',
        slugify=custom_slugify,
    )
    customizations = JSONField(
        _('Customizations'),
        default={},
    )
    has_tour = models.BooleanField(
        _('Has User Tour'),
        default=True,
    )
    is_login_required = models.BooleanField(
        _('Is Login Required'),
        default=True,
    )
    image = models.ImageField(
        _('Image'),
        upload_to='conversations/categories',
        null=True, blank=True,
    )
    image_caption = models.CharField(
        _('Image caption'),
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('created_at',)

    def __str__(self):
        return self.name
