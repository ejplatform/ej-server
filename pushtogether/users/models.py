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

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    email = models.EmailField(_('Email'), null=True)
    city = models.CharField(_('City'), null=True, max_length=255)
    state = models.CharField(_('State'), null=True, max_length=255)
    country = models.CharField(_('Country'), null=True, max_length=255)
    occupation = models.CharField(_('Occupation'), null=True, max_length=255)
    age = models.IntegerField(_('Age'), null=True, blank=True)
    gender = models.CharField(
        _('Gender'),
        null=True,
        choices=GENDER_CHOICES,
        max_length=255
    )
    gender_other = models.CharField(
        _('Other type of gender'),
        null=True, max_length=255
    )
    political_movement = models.CharField(
        _('Participates in any political movement?'),
        null=True,
        max_length=255
    )
    race = models.CharField(
        _('Race'),
        null=True,
        choices=RACE_CHOICES,
        max_length=255
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    @property
    def image_url(self):
        social_accounts = SocialAccount.objects.filter(user_id=self.id)

        for account in social_accounts:
            picture = account.get_avatar_url()
            if picture:
                return picture
        return "https://gravatar.com/avatar/{}?s=40&d=mm".format(hashlib.md5(self.email.encode('utf-8')).hexdigest())
