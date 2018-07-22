import hashlib

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ugettext as __
from sidekick import delegate_to
from boogie.fields import EnumField
from boogie.rest import rest_api
from .choices import Race, Gender
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

@rest_api(exclude=['user'])
class Profile(models.Model):
    """
    User profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='raw_profile')
    race = EnumField(Race, _('Race'), default=Race.UNDECLARED)
    gender = EnumField(Gender, _('Gender identity'), default=Gender.UNDECLARED)
    gender_other = models.CharField(_('User provided gender'), max_length=50, blank=True)
    age = models.IntegerField(_('Age'), blank=True, default=0)
    phone = models.CharField(_('Phone'), blank=True, max_length=50)
    country = models.CharField(_('Country'), blank=True, max_length=50)
    state = models.CharField(_('State'), blank=True, max_length=140)
    city = models.CharField(_('City'), blank=True, max_length=140)
    biography = models.TextField(_('Biography'), blank=True)
    occupation = models.CharField(_('Occupation'), blank=True, max_length=50)
    political_activity = models.TextField(_('Political activity'), blank=True)
    image = models.ImageField(_('Image'), blank=True, null=True, upload_to='profile_images')

    name = delegate_to('user')
    username = delegate_to('user')
    email = delegate_to('user')
    is_active = delegate_to('user')
    is_staff = delegate_to('user')
    is_superuser = delegate_to('user')

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return __('{name}\'s profile').format(name=self.user.name)

    def __getattr__(self, attr):
        try:
            user = self.user
        except User.DoesNotExist:
            raise AttributeError(attr)
        return getattr(user, attr)

    @property
    def gender_description(self):
        if self.gender != Gender.UNDECLARED:
            return self.gender.description
        return self.gender_other

    @property
    def token(self):
        token = Token.objects.get_or_create(user_id=self.id)
        return token[0].key

    @property
    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            for account in SocialAccount.objects.filter(user_id=self.id):
                picture = account.get_avatar_url()
                if picture:
                    return picture
            return avatar_fallback()

    @property
    def has_image(self):
        return self.image or SocialAccount.objects.filter(user_id=self.id)

    @property
    def is_filled(self):
        fields = ('race', 'age', 'country', 'state', 'city', 'biography', 'phone',
                  'occupation', 'political_activity', 'has_image', 'gender_description')
        return bool(all(getattr(self, field) for field in fields))

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.id})

    def profile_fields(self, user_fields=False):
        """
        Return a list of tuples of (field_description, field_value) for all
        registered profile fields.
        """

        fields = ['city', 'country', 'occupation', 'age', 'phone', 'gender', 'race', 'political_activity', 'biography']
        field_map = {field.name: field for field in self._meta.fields}
        result = []
        for field in fields:
            description = field_map[field].verbose_name
            getter = getattr(self, f'get_{field}_display', lambda: getattr(self, field))
            result.append((description.capitalize(), getter()))
        if user_fields:
            result = [
                (_('E-mail'), self.user.email),
                *result,
            ]
        return result

    def statistics(self):
        """
        Return a dictionary with all profile statistics.
        """
        return dict(
            votes=self.user.votes.count(),
            comments=self.user.comments.count(),
            conversations=self.user.conversations.count(),
        )

    def badges(self):
        """
        Return all profile badges.
        """
        return self.user.badges_earned.all()

    def comments(self):
        """
        Return all profile comments.
        """
        return self.user.comments.all()

    def role(self):
        """
        A human-friendly description of the user role in the platform.
        """
        if self.user.is_superuser:
            return _('Root')
        if self.user.is_staff:
            return _('Administrative user')
        return _('Regular user')


@rest_api(exclude=['profile'])
class Setting(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    owner_id = models.IntegerField(null=True)
    mission_notifications = models.BooleanField(default=True)
    conversation_notifications = models.BooleanField(default=True)
    admin_notifications = models.BooleanField(default=True)
    trophy_notifications = models.BooleanField(default=True)
    approved_notifications = models.BooleanField(default=True)
    disapproved_notifications = models.BooleanField(default=True)
    campaign_email = models.BooleanField(default=True)
    campaign_app_notifications = models.BooleanField(default=True)
    share_data = models.BooleanField(default=True)
    

def gravatar_fallback(id):
    """
    Computes gravatar fallback image URL from a unique string identifier
    """
    digest = hashlib.md5(id.encode('utf-8')).hexdigest()
    return "https://gravatar.com/avatar/{}?s=40&d=mm".format(digest)


def avatar_fallback():
    """
    Return fallback image URL for profile
    """
    return "/static/img/logo/avatar_default.svg"


def get_profile(user):
    """
    Return profile instance for user. Create profile if it does not exist.
    """
    try:
        return user.profile
    except Profile.DoesNotExist:
        return Profile.objects.create(user=user)

User.get_profile = get_profile

@receiver(post_save, sender=Profile)
def ensure_settings_created(sender, **kwargs):
    instance = kwargs.get('instance')
    profile = instance.id
    return Setting.objects.create(profile=instance, owner_id=profile)

