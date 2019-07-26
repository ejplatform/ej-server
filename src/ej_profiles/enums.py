from boogie.fields import IntEnum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from environ import ImproperlyConfigured

_race_enums = getattr(settings, "EJ_PROFILE_RACE_CHOICES", None)
_gender_enums = getattr(settings, "EJ_PROFILE_GENDER_CHOICES", None)
_not_filed = getattr(settings, "EJ_NOT_FILLED_MARK", "---------")

# Here we fool the IntEnum metaclass into believing that items of a list are
# methods
_to_thunks = lambda lst: ((lambda: k, lambda: v) for k, v in lst)


class Race(IntEnum):
    NOT_FILLED = 0, _not_filed

    if _race_enums is None:
        BLACK = 1, _("Black")
        BROWN = 2, _("Brown")
        WHITE = 3, _("White")
        YELLOW = 4, _("Yellow")
        INDIGENOUS = 5, _("Indigenous")
        OTHER = 6, _("Other")
    else:
        for _k, _v in _to_thunks(_race_enums.items()):
            locals()[_k()] = _v()


class Gender(IntEnum):
    NOT_FILLED = 0, _not_filed

    if _gender_enums is None:
        FEMALE = 1, _("Female")
        MALE = 2, _("Male")
        OTHER = 20, _("Other")
    else:
        for _k, _v in _to_thunks(_gender_enums.items()):
            locals()[_k()] = _v()


STATE_CHOICES = getattr(settings, "EJ_PROFILE_STATE_CHOICES", {})
STATE_CHOICES_MAP = dict(STATE_CHOICES)
if not STATE_CHOICES:
    raise ImproperlyConfigured(
        "You must define the environment variable EJ_PROFILE_STATE_CHOICES in " "your Django settings."
    )
