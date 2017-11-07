from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from allauth.socialaccount.models import SocialAccount
import hashlib


class User(AbstractUser):

    RACE_CHOICES = (
        ('BLACK', _('Black')),
        ('BROWN', _('Brown')),
        ('WHITE', _('White')),
        ('YELLOW', _('Yellow')),
        ('INDIGENOUS', _('Indigenous')),
        ('DO_NOT_KNOW', _('Do not know')),
        ('UNDECLARED', _('Undeclared')),
    )

    GENDER_CHOICES = (
        ('FEMALE', _('Female')),
        ('MALE', _('Male')),
        ('CIS_FEMALE', _('Cis Female')),
        ('CIS_MALE', _('Cis Male')),
        ('AGENDER', _('Agender')),
        ('GENDERQUEER', _('Genderqueer')),
        ('GENDERFLUID', _('Genderfluid')),
        ('NON-CONFORMIST_GENDER', _('Non conformist gender')),
        ('VARIANT_GENDER', _('Variant gender')),
        ('INTERSEX', _('Intersex')),
        ('NON-BINARY', _('Non binary')),
        ('TRANSGENDERED', _('Transgendered')),
        ('PANGENDER', _('Pangender')),
        ('TRANSSEXUAL_WOMAN', _('Transsexual woman')),
        ('TRANSSEXUAL_MAN', _('Transsexual man')),
        ('TRANSFEMINAL', _('Transfeminal')),
        ('TRANSMASCULINE', _('Transmasculine')),
        ('DO_NOT_KNOW', _('Do not know')),
        ('NONE', _('None')),
        ('OTHER', _('Other'))
    )

    age = models.IntegerField(_('Age'), null=True, blank=True)
    city = models.CharField(_('City'), null=True, blank=True, max_length=255)
    state = models.CharField(_('State'), null=True, blank=True, max_length=255)
    biography = models.TextField(_('Biography'), blank=True, null=True)
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(
        _('Name of User'),
        blank=True,
        max_length=255,
        null=True
    )
    country = models.CharField(
        _('Country'),
        null=True,
        blank=True,
        max_length=255
    )
    occupation = models.CharField(
        _('Occupation'),
        null=True,
        blank=True,
        max_length=255
    )
    image = models.ImageField(
        _('Image'),
        blank=True,
        null=True,
        upload_to='profile_images'
    )
    gender = models.CharField(
        _('Gender'),
        null=True,
        choices=GENDER_CHOICES,
        max_length=255,
        blank=True
    )
    gender_other = models.CharField(
        _('Other type of gender'),
        null=True, max_length=255,
        blank=True
    )
    political_movement = models.CharField(
        _('Participates in any political movement?'),
        null=True,
        blank=True,
        max_length=255
    )
    race = models.CharField(
        _('Race'),
        null=True,
        blank=True,
        choices=RACE_CHOICES,
        max_length=255
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        social_accounts = SocialAccount.objects.filter(user_id=self.id)

        for account in social_accounts:
            picture = account.get_avatar_url()
            if picture:
                return picture
        return "https://gravatar.com/avatar/{}?s=40&d=mm".format(hashlib.md5(self.email.encode('utf-8')).hexdigest())
