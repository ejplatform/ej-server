from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from allauth.socialaccount.models import SocialAccount
import hashlib


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)

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
        return "http://www.gravatar.com/avatar/{}?s=40".format(hashlib.md5(self.email).hexdigest())
