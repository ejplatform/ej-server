from django.db import models
from django.utils.translation import ugettext_lazy as _
import bleach
from ej_conversations.validators import validate_color
from .icons import default_icon_name
from .validators import validate_icon_name


class SocialMediaIcon(models.Model):
    ICON_MATERIAL = 'material'
    ICON_AWESOME = 'fa'
    ICON_CHOICES = (
        (ICON_MATERIAL, _('Material Design')),
        (ICON_AWESOME, _('Font-awesome')),
    )
    social_network = models.CharField(
        _('Social network'),
        max_length=50,
        unique=True,
        help_text=_('Name of the social network'),
    )
    icon_name = models.CharField(
        _('Icon name'),
        max_length=50,
        help_text=_('Icon name for the icon font'),
    )
    icon_font = models.CharField(
        _('Icon font'),
        max_length=10,
        default=ICON_AWESOME,
    )
    ordering = models.PositiveSmallIntegerField(
        _('Ordering'),
        unique=True,
        help_text=_(
            'You must manually define the ordering that each icon should '
            'appear in the interface.'
        ),
    )
    url = models.URLField(
        _('URL'),
        help_text=_('Link to your social account page.')
    )

    def __str__(self):
        return self.social_network

    def __html__(self):
        return self.link_tag()

    def clean(self):
        # We want to set the default icon for the most common social networks.
        # TODO: see if this works!
        if not self.icon_name:
            self.icon_name = default_icon_name(self.social_network)

        if self.icon_font == self.ICON_MATERIAL:
            validate_icon_name(self.icon_name, 'material')
        elif self.icon_font == self.ICON_AWESOME:
            validate_icon_name(self.icon_name, 'fa')

    def icon_tag(self, classes=()):
        """
        Render an icon tag for the given icon.

        >>> icon.icon_tag(classes=['header-icon'])
        <i class="fa fa-icon header-icon"></i>
        """
        
        return f'<i class="{self.icon_font} {" ".join(classes)}"></i>'

    def link_tag(self, classes=()):
        """
        Render an anchor tag with the link for the social network.

        >>> icon.link_tag(classes=['header-icon'])
        <a href="url"><i class="fa fa-icon header-icon"></i></a>
        """          

        return f'<a href="{self.url}"><i class="{self.icon_font} {" ".join(classes)}"></i></a>'


class Color(models.Model):
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
        return f'self.name ({self.hex_value})'


class Fragment(models.Model):
    FORMAT_MARKDOWN = 'md'
    FORMAT_HTML = 'html'
    ...

    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
        db_index=True,
        help_text=_('Name of the fragment to help identify some page part.'),
    )
    content = models.TextField(
        _('content'),
        blank=True,
        help_text=_('The fragment content in html or markdown that will be displayed')
    )
    format = models.CharField(
        max_length=4,
        help_text=_('Format of the saved fragment, can be html or md')
    )
    editable = models.BooleanField(
        default=True,
        help_text=_('Boolean if the fragment its editable after being saved in db'),
    )
    deletable = models.BooleanField(
        default=True,
        help_text=_('Boolean if its possible to delete this fragment'),
    )

    def __html__(self):
        return self.html()

    def __str__(self):
        return self.name.replace('_', ' ').replace('-', ' ').replace('/', '').capitalize()

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
        if not self.deletable:
            # conferir se levanta erro .DoesNotExist
            if self.lock is None:
                FragmentLock.objects.create(self)

    def html(self, classes=()):
        data = sanitize_html(self.content)
        #data = self.content
        class_attr = " ".join(classes)
        return f'<div{class_attr}>{data}</div>'


def sanitize_html(html):
    return bleach.clean(html, tags=['h1','h2','h3','h4','a','p','i','img','strong','div'])


# GAMBIRA!
class FragmentLock(models.Model):
    fragment = models.OneToOneField(
        Fragment,
        on_delete=models.PROTECT,
        related_name='lock',
    )
