from django.db import models
from django.utils.translation import ugettext_lazy as _
from markupsafe import Markup

from ej_conversations.validators import validate_color
from .icons import default_icon_name
from .sanitizer import sanitize_html
from .validators import validate_icon_name


class SocialMediaIcon(models.Model):
    """
    Configurable reference to a social media icon.
    """
    social_network = models.CharField(
        _('Social network'),
        max_length=50,
        unique=True,
        help_text=_('Name of the social network (e.g., Facebook)'),
    )
    icon_name = models.CharField(
        _('Icon name'),
        max_length=50,
        help_text=_('Icon name in font-awesome'),
        validators=[validate_icon_name],
    )
    index = models.PositiveSmallIntegerField(
        _('Ordering'),
        default=0,
        help_text=_(
            'You can manually define the ordering that each icon should '
            'appear in the interface. Otherwise, icons will be shown in '
            'insertion order.'
        ),
    )
    url = models.URLField(
        _('URL'),
        help_text=_('Link to your social account page.')
    )

    class Meta:
        ordering = ['index', 'id']
        verbose_name = _('Social media icon')
        verbose_name_plural = _('Social media icons')

    def __str__(self):
        return self.social_network

    def __html__(self):
        return self.link_tag()

    def clean(self):
        if not self.icon_name:
            self.icon_name = default_icon_name(self.social_network.casefold())

    def icon_tag(self, classes=()):
        """
        Render an icon tag for the given icon.

        >>> icon.icon_tag(classes=['header-icon'])              # doctest: +SKIP
        <i class="fa fa-icon header-icon"></i>
        """
        classes = [self.icon_name, *classes]
        return f'<i {class_string(classes)}"></i>'

    def link_tag(self, classes=(), icon_classes=()):
        """
        Render an anchor tag with the link for the social network.

        >>> icon.link_tag(classes=['header-icon'])              # doctest: +SKIP
        <a href="url"><i class="fa fa-icon header-icon"></i></a>
        """
        classes = class_string(classes)
        return f'<a href="{self.url}"{classes}>{self.icon_tag(icon_classes)}</a>'


class Color(models.Model):
    """
    Generic color reference that can be configured in the admin interface.
    """
    name = models.CharField(
        _('Color name'),
        max_length=150,
    )
    hex_value = models.CharField(
        _('Color'),
        max_length=30,
        help_text=_(
            'Color code in hex (e.g., #RRGGBBAA) format.'
        ),
        validators=[validate_color],
    )

    def __str__(self):
        return f'{self.name}: {self.hex_value}'

    def __html__(self):
        return self.hex_value


class Fragment(models.Model):
    """
    Configurable HTML fragments that can be inserted in pages.
    """

    FORMAT_MARKDOWN = 'md'
    FORMAT_HTML = 'html'
    FORMAT_CHOICES = [
        (FORMAT_HTML, _('HTML')),
        (FORMAT_MARKDOWN, _('Markdown')),
    ]

    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_('Unique identifier for fragment name'),
    )
    format = models.CharField(
        max_length=4,
        choices=FORMAT_CHOICES,
    )
    content = models.TextField(
        _('content'),
        blank=True,
        help_text=_('Raw fragment content in HTML or Markdown'),
    )
    editable = models.BooleanField(
        default=True,
        editable=False,
    )

    def __html__(self):
        return self.html()

    def __str__(self):
        return self.name

    def lock(self):
        """
        Prevents fragment from being deleted.
        """
        FragmentLock.objects.update_or_create(fragment=self)

    def unlock(self):
        """
        Allows fragment being deleted.
        """
        FragmentLock.objects.filter(fragment=self).delete()

    def html(self, classes=()):
        data = sanitize_html(self.content)
        class_attr = " ".join(classes)
        return Markup(f'<div{class_attr}>{data}</div>')


class FragmentLock(models.Model):
    """
    ForeignKey reference that prevents protected fragments from being deleted
    from the database.
    """
    fragment = models.OneToOneField(
        Fragment,
        on_delete=models.PROTECT,
        related_name='lock_ref',
    )


def class_string(class_list):
    if class_list:
        class_ = ' '.join(class_list)
        return f' class="{class_}"'
    else:
        return ''
