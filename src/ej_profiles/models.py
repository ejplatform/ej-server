import hashlib

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ugettext as __
from rest_framework.authtoken.models import Token
import datetime

from boogie.fields import EnumField
from boogie.rest import rest_api
from sidekick import delegate_to
from .choices import Race, Gender

User = get_user_model()


@rest_api(exclude=['user'])
class Profile(models.Model):
    """
    User profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='raw_profile')
    race = EnumField(Race, _('Race'), default=Race.UNDECLARED)
    ethnicity = models.CharField(_('Ethnicity'), blank=True, max_length=50)
    education = models.CharField(_('Education'), blank=True, max_length=140)
    gender = EnumField(Gender, _('Gender identity'), default=Gender.UNDECLARED)
    gender_other = models.CharField(_('User provided gender'), max_length=50, blank=True)
    age = models.IntegerField(_('Age'), null=True, blank=True)
    birth_date = models.DateField(_('Birth Date'), null=True, blank=True)
    country = models.CharField(_('Country'), blank=True, max_length=50)
    state = models.CharField(_('State'), blank=True, max_length=140)
    city = models.CharField(_('City'), blank=True, max_length=140)
    biography = models.TextField(_('Biography'), blank=True)
    occupation = models.CharField(_('Occupation'), blank=True, max_length=50)
    political_activity = models.TextField(_('Political activity'), blank=True)
    image = models.ImageField(_('Image'), blank=True, null=True, upload_to='profile_images')

    name = delegate_to('user')
    email = delegate_to('user')
    is_active = delegate_to('user')
    is_staff = delegate_to('user')
    is_superuser = delegate_to('user')

    @property
    def age(self):
        if not self.birth_date:
            age = None
        else:
            delta = datetime.datetime.now().date() - self.birth_date
            age = abs(int(delta.days // 365.25))
        return age

    class Meta:
        ordering = ['user__email']

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
            return '/static/img/logo/avatar_default.svg'

    @property
    def has_image(self):
        return self.image or SocialAccount.objects.filter(user_id=self.id)

    @property
    def is_filled(self):
        fields = ('race', 'age', 'birth_date', 'education', 'ethnicity', 'country', 'state', 'city',
                  'biography', 'occupation', 'political_activity', 'has_image', 'gender_description')
        return bool(all(getattr(self, field) for field in fields))

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.id})

    def profile_fields(self, user_fields=False):
        """
        Return a list of tuples of (field_description, field_value) for all
        registered profile fields.
        """

        fields = ['city', 'country', 'occupation', 'education', 'ethnicity', 'gender', 'race',
                  'political_activity', 'biography']
        field_map = {field.name: field for field in self._meta.fields}
        result = []
        for field in fields:
            description = field_map[field].verbose_name
            getter = getattr(self, f'get_{field}_display', lambda: getattr(self, field))
            result.append((description.capitalize(), getter()))

        age = (_('Age'), self.age)
        result.insert(3, age)
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


def gravatar_fallback(id):
    """
    Computes gravatar fallback image URL from a unique string identifier
    """
    digest = hashlib.md5(id.encode('utf-8')).hexdigest()
    return "https://gravatar.com/avatar/{}?s=40&d=mm".format(digest)


def get_profile(user):
    """
    Return profile instance for user. Create profile if it does not exist.
    """
    try:
        return user.profile
    except Profile.DoesNotExist:
        return Profile.objects.create(user=user)


User.get_profile = get_profile
