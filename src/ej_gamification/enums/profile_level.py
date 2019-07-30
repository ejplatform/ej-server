from boogie.fields import IntEnum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ngettext, ugettext as __

from ej_profiles.enums import Race, Gender
from ej_profiles.forms import EDITABLE_FIELDS as PROFILE_EDITABLE_FIELDS
from ej_profiles.models import get_profile
from ._base import LevelMixin

PROFILE_LEVELS = getattr(
    settings, "EJ_GAMIFICATION_PROFILE_LEVELS", [_("Basic"), _("Relevant"), _("Informative"), _("Complete")]
)


class ProfileLevel(LevelMixin, IntEnum):
    """
    PROFILE TRACK

    User gain points for filling in profile information.

    The test function receives an instance of Profile.
    """

    NONE = 0, _("No level")
    PROFILE_LVL1 = 1, PROFILE_LEVELS[0]
    PROFILE_LVL2 = 2, PROFILE_LEVELS[1]
    PROFILE_LVL3 = 3, PROFILE_LEVELS[2]
    PROFILE_LVL4 = 4, PROFILE_LEVELS[3]

    @classmethod
    def check_level(cls, data):
        fields = set(PROFILE_EDITABLE_FIELDS)
        profile = get_profile(data.user)
        level = cls.NONE

        # First level: user completed the site tour.
        if True:
            level = cls.PROFILE_LVL1
        else:
            return level

        # Second level: user uploaded a photo and filled drop-downs.
        if profile.profile_photo and filled_gender_and_race(profile, fields):
            level = cls.PROFILE_LVL2
        else:
            return level

        # Third level: all one-liner fields.
        if filled_fields(profile, basic_profile_fields(fields)):
            level = cls.PROFILE_LVL3
        else:
            return level

        # Last level: user filled *ALL* profile info.
        if filled_gender_and_race(profile, fields) and filled_fields(profile, fields):
            level = cls.PROFILE_LVL4
        return level

    def achieve_next_level_msg(self, data):
        p = get_profile(data.user)
        fields = set(PROFILE_EDITABLE_FIELDS)

        if self == self.PROFILE_LVL4:
            return _("Congratulations! Your profile is complete!")

        elif self == self.NONE:
            return _("Please take the site tour!")

        elif self == self.PROFILE_LVL1:
            missing = []
            if "race" in fields and p.race == Race.NOT_FILLED:
                missing.append(_("race"))
            if "gender" in fields and p.gender == Gender.NOT_FILLED:
                missing.append(_("gender"))
            if not p.profile_photo:
                missing.append(_("profile photo"))
            if missing:
                return missing_fields_message(missing[:3])

        elif self == self.PROFILE_LVL2:
            fields_ = basic_profile_fields(fields)
            return missing_fields_message(missing_fields(p, fields_))

        elif self == self.PROFILE_LVL3:
            return missing_fields_message(missing_fields(p, fields))


def filled_gender_and_race(p, fields):
    if "race" in fields and p.race == Race.NOT_FILLED:
        return False
    if "gender" in fields and p.gender == Gender.NOT_FILLED:
        return False
    return True


def filled_fields(profile, fields):
    is_filled = lambda f: f is not None and f != ""
    return all(is_filled(getattr(profile, f)) for f in fields)


def basic_profile_fields(fields):
    basic = {"gender", "race", "birth_date", "occupation", "city", "state", "country", "education"}
    return fields.intersection(basic)


def missing_fields(profile, fields):
    missing = []
    for field in fields:
        if getattr(profile, field, None) in (None, ""):
            missing.append(_(field.replace("_", " ")))
    return missing[:3]


def missing_fields_message(fields):
    data = fields[0] if len(fields) == 1 else humanize_list(fields)
    return ngettext(
        "Please fill up the {} field of your profile",
        "Please fill up the {} fields of your profile",
        len(fields),
    ).format(data)


def humanize_list(lst):
    if not lst:
        return ""
    lst = lst.copy()
    last = lst.pop()
    return __("{} and {}").format(", ".join(map(str, lst)), last)
