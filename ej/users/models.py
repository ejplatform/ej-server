import hashlib

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    TOUR_CHOICES = (
        ('STEP_ONE', _('Step One')),
        ('STEP_TWO', _('Step Two')),
        ('STEP_THREE', _('Step Three')),
        ('STEP_FOUR', _('Step Four')),
        ('STEP_FIVE', _('Step Five')),
        ('STEP_SIX', _('Step Six')),
        ('STEP_SEVEN', _('Step Seven')),
        ('STEP_EIGHT', _('Step Eight')),
        ('STEP_NINE', _('Step Nine')),
        ('STEP_TEN', _('Step Ten')),
        ('STEP_FINISH', _('Final Step')),
    )

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
        _('Name'),
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
        _('User provided gender'),
        null=True,
        max_length=255,
        blank=True
    )
    political_movement = models.TextField(
        _('Political activity'),
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
    tour_step = models.CharField(
        _('Current tour step'),
        null=True,
        blank=True,
        choices=TOUR_CHOICES,
        max_length=255
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('v1:user-detail', kwargs={'pk': self.id})

    @property
    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            for account in SocialAccount.objects.filter(user_id=self.id):
                picture = account.get_avatar_url()
                if picture:
                    return picture
            return gravatar_fallback(self.email)

    @property
    def profile_filled(self):
        filled_image = self.image or SocialAccount.objects.filter(user_id=self.id)
        filled_gender = (self.gender or self.gender_other)
        return bool(filled_image and self.age and self.city and self.state and self.biography and self.name and
                    self.country and self.occupation and filled_gender and self.political_movement and self.race)


def gravatar_fallback(id):
    "Computes gravatar fallback image URL from a unique string identifier"

    return "https://gravatar.com/avatar/{}?s=40&d=mm".format(hashlib.md5(id.encode('utf-8')).hexdigest())
