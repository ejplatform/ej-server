from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from allauth.socialaccount.models import SocialAccount
import hashlib

class User(AbstractUser):

    RACE_CHOICES = (
        ('BLACK', 'Preta'),
        ('BROWN', 'Parda'),
        ('WHITE', 'Branca'),
        ('YELLOW', 'Amarela'),
        ('INDIGENOUS', 'Indígena'),
        ('DO_NOT_KNOW', 'Não sei'),
        ('UNDECLARED', 'Não declarada'),
    )

    GENDER_CHOICES = (
        ('FEMALE', 'Mulher'),
        ('MALE', 'Homem'),
        ('CIS_FEMALE', 'Mulher Cis'),
        ('CIS_MALE', 'Homem Cis'),
        ('AGENDER', 'Agênero'),
        ('GENDERQUEER', 'Genderquer'),
        ('GENDERFLUID', 'Gênero Fluído'),
        ('NON-CONFORMIST_GENDER', 'Gênero Não-conformista'),
        ('VARIANT_GENDER', 'Gênero Variante'),
        ('INTERSEX', 'Intersex'),
        ('NON-BINARY', 'Não-binário'),
        ('TRANSGENDERED', 'Transgênero'),
        ('PANGENDER', 'Pangênero'),
        ('TRANSSEXUAL_WOMAN', 'Mulher Transexual'),
        ('TRANSSEXUAL_MAN', 'Homem Transexual'),
        ('TRANSFEMINAL', 'Transfeminino'),
        ('TRANSMASCULINE', 'Transmasculino'),
        ('DO_NOT_KNOW', 'Não sei'),
        ('NONE', 'Nenhum'),
        ('OTHER', 'Outro')
    )

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    email = models.EmailField(null=True)
    city = models.CharField(null=True, max_length=255)
    state = models.CharField(null=True, max_length=255)
    country = models.CharField(null=True, max_length=255)
    race = models.CharField(null=True, choices=RACE_CHOICES, max_length=255)
    gender = models.CharField(null=True, choices=GENDER_CHOICES, max_length=255)
    gender_other = models.CharField(null=True, max_length=255)
    occupation = models.CharField(null=True, max_length=255)
    age = models.IntegerField(null=True, blank=True)
    political_movement = models.CharField(null=True, max_length=255)

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
