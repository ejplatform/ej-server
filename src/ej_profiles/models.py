import hashlib

from boogie.fields import EnumField
from boogie.rest import rest_api
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ugettext as __
from rest_framework.authtoken.models import Token
from sidekick import delegate_to, import_later

from .enums import Race, Gender, STATE_CHOICES_MAP
from .utils import years_from

SocialAccount = import_later("allauth.socialaccount.models:SocialAccount")
User = get_user_model()


@rest_api(exclude=["user"])
class Profile(models.Model):
    """
    User profile
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    race = EnumField(Race, _("Race"), default=Race.NOT_FILLED)
    ethnicity = models.CharField(_("Ethnicity"), blank=True, max_length=50)
    education = models.CharField(_("Education"), blank=True, max_length=140)
    gender = EnumField(Gender, _("Gender identity"), default=Gender.NOT_FILLED)
    gender_other = models.CharField(_("User provided gender"), max_length=50, blank=True)
    birth_date = models.DateField(_("Birth Date"), null=True, blank=True)
    country = models.CharField(_("Country"), blank=True, max_length=50)
    state = models.CharField(_("State"), blank=True, max_length=3)
    city = models.CharField(_("City"), blank=True, max_length=140)
    biography = models.TextField(_("Biography"), blank=True)
    occupation = models.CharField(_("Occupation"), blank=True, max_length=50)
    political_activity = models.TextField(_("Political activity"), blank=True)
    profile_photo = models.ImageField(_("Profile Photo"), blank=True, null=True, upload_to="profile_images")

    name = delegate_to("user")
    email = delegate_to("user")
    is_active = delegate_to("user")
    is_staff = delegate_to("user")
    is_superuser = delegate_to("user")
    limit_board_conversations = delegate_to("user")

    basic_fields = [
        "city",
        "state",
        "country",
        "occupation",
        "education",
        "ethnicity",
        "gender",
        "race",
        "political_activity",
        "biography",
    ]

    @property
    def age(self):
        return None if self.birth_date is None else years_from(self.birth_date)

    class Meta:
        ordering = ["user__email"]

    def __str__(self):
        return __("{name}'s profile").format(name=self.user.name)

    def __getattr__(self, attr):
        try:
            user = self.user
        except User.DoesNotExist:
            raise AttributeError(attr)
        return getattr(user, attr)

    @property
    def gender_description(self):
        if self.gender != Gender.NOT_FILLED:
            return self.gender.description
        return self.gender_other

    @property
    def token(self):
        token = Token.objects.get_or_create(user_id=self.id)
        return token[0].key

    @property
    def image_url(self):
        try:
            return self.profile_photo.url
        except ValueError:
            if apps.is_installed("allauth.socialaccount"):
                for account in SocialAccount.objects.filter(user=self.user):
                    picture = account.get_avatar_url()
                    return picture
            return staticfiles_storage.url("/img/login/avatar.svg")

    @property
    def has_image(self):
        return bool(
            self.profile_photo
            or (
                apps.is_installed("allauth.socialaccount") and SocialAccount.objects.filter(user_id=self.id)
            )
        )

    @property
    def is_filled(self):
        fields = self.basic_fields
        fields[fields.index('gender')] = 'gender_orientation'
        fields = tuple(fields) + (
             "age",
             "birth_date",
             "has_image",
        )
        return bool(all(getattr(self, field) for field in fields))

    def get_absolute_url(self):
        return reverse("user-detail", kwargs={"pk": self.id})

    def create_tuple_of_interest(self, fields, null_values):
        """
        Return a tuples of (attribute, human-readable name, value)
        """
        field_map = {field.name: field for field in self._meta.fields}
        triple_list = []
        for field in fields:
            description = field_map[field].verbose_name
            value = getattr(self, field)
            if value in null_values:
                value = None
            elif hasattr(self, f"get_{field}_display"):
                value = getattr(self, f"get_{field}_display")()
            triple_list.append((field, description, value))
        return triple_list

    def profile_fields(self, user_fields=False, blacklist=None):
        """
        Return a list of tuples of (field_description, field_value) for all
        registered profile fields.
        """

        fields = self.basic_fields
        null_values = {Gender.NOT_FILLED, Race.NOT_FILLED, None, ""}

        # Create a tuples of (attribute, human-readable name, value)
        triple_list = create_tuple_of_interest(self, fields, null_values)
        
        # Age is not a real field, but a property. We insert it after occupation
        triple_list.insert(3, ("age", _("Age"), self.age))

        # Add fields in the user profile (e.g., e-mail)
        if user_fields:
            triple_list.insert(0, ("email", _("E-mail"), self.user.email))

        # Prepare blacklist of fields and overrides
        if blacklist is None:
            blacklist = settings.EJ_PROFILE_EXCLUDE_FIELDS
        name_overrides = getattr(settings, "EJ_PROFILE_FIELD_NAMES", {})

        return list(prepare_fields(triple_list, blacklist, name_overrides))

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
            return _("Root")
        if self.user.is_staff:
            return _("Administrative user")
        return _("Regular user")

    def get_state_display(self):
        return STATE_CHOICES_MAP.get(self.state, self.state) or _("(Not Filled)")


def prepare_fields(triples, blacklist, overrides):
    for a, b, c in triples:
        if a in blacklist:
            continue
        b = overrides.get(a, b)
        yield b, c


def gravatar_fallback(id_):
    """
    Computes gravatar fallback image URL from a unique string identifier
    """
    digest = hashlib.md5(id_.encode("utf-8")).hexdigest()
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
