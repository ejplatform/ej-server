import hashlib
import random
import string

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models, IntegrityError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def get_by_email_or_username(self, value):
        """
        Return a user with the given e-mail or username.
        """
        if '@' in value:
            return self.get(email=value)
        else:
            return self.get(username=value)

    def create_simple_user(self, name, email, password):
        """
        Create standard user from name, email and password.
        """
        if self.filter(email=email):
            raise IntegrityError(f'user with email {email} already exists')

        first_name, _, last_name = name.partition(' ')
        username = self.available_username(name, email)
        user = self.create(
            name=name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            username=username,
        )
        user.set_password(password)
        user.save()
        return user

    def available_username(self, name, email):
        """
        Return an available username from name and e-mail information.
        """
        username, _, domain = email.partition('@')
        domain = domain.replace('-', '_')
        domain = domain.replace('.com', '')
        first_name = name.lower().partition(' ')[0]
        last_name = name.lower().partition(' ')[-1]
        last_name = last_name.replace(' ', '_')

        tests = [
            username,
            first_name,
            last_name,
            last_name + '_' + domain,
            username + '_' + domain,
        ]

        existing = set(
            self.filter(username__in=tests)
                .values_list('username', flat=True)
        )
        available = [name for name in tests if name not in existing]
        if available:
            return available[0]

        names = set(
            self
                .filter(username__startswith=username)
                .values_list('username', flat=True)
        )
        for i in range(1000):
            test = '%s_%s' % (username, i)
            if test not in names:
                return test
        return random_username()


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
        _('Gender identity'),
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
    objects = UserManager()

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.id})

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

    def get_profile_fields(self):
        """
        Return a list of tuples of (field_description, field_value) for all registered profile
        fields.
        """

        fields = ['email', 'city', 'country', 'occupation', 'age', 'gender', 'race', 'political_movement', 'city']
        field_map = {field.name: field for field in self._meta.fields}
        result = []
        for field in fields:
            description = field_map[field].verbose_name
            getter = getattr(self, f'get_{field}_display', lambda: getattr(self, field))
            result.append((description.capitalize(), getter()))
        return result

    def get_profile_statistics(self):
        """
        Return a dictionary with all profile statistics.
        """
        return dict(
            votes=self.votes.count(),
            comments=self.comments.count(),
            conversations=self.conversations.count(),
        )

    def get_role_description(self):
        """
        A human-friendly description of the user role in the platform.
        """
        if self.is_superuser:
            return _('Root')
        if self.is_staff:
            return _('Administrative user')
        return _('Regular user')



def gravatar_fallback(id):
    "Computes gravatar fallback image URL from a unique string identifier"

    return "https://gravatar.com/avatar/{}?s=40&d=mm".format(hashlib.md5(id.encode('utf-8')).hexdigest())


def random_username():
    "A random username value with very low collision probability"

    return ''.join(random.choice(string.ascii_letters) for _ in range(20))
