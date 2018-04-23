# from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SocialMedia(models.Model):
    ICON_CHOICES = (
        ('MATERIAL', _('Material icon')),
        ('FONT_AWESOME', _('Font-awesome icon')),
    )

    name = models.CharField(_('Name'), blank=True, max_length=255, null=True)
    material_icon = models.CharField(_('Material_icon'), blank=True, max_length=255, null=True)
    fa_icon = models.CharField(_('FA_icon'), blank=True, max_length=255, null=True)
    priority = models.IntegerField(_('Priority'), null=True, blank=True)
    link = models.CharField(_('Link'), null=True, blank=True, max_length=255)

    def __str__(self):
        return self.name


class ColorPallete(models.Model):
    name = models.CharField(_('Name'), blank=True, max_length=255, null=True)
    # colors = ArrayField(models.CharField(_('RGBA'), blank=True, max_length=255, null=True), blank=False)

    def __str__(self):
        return self.name
