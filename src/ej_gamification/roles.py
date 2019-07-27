from django.utils.translation import ugettext_lazy as _

from ej.roles import with_template
from . import enums
from .models import UserProgress, ParticipationProgress, ConversationProgress

LEVEL_TYPES = (
    enums.ConversationLevel,
    enums.VoterLevel,
    enums.CommenterLevel,
    enums.HostLevel,
    enums.ProfileLevel,
    enums.ScoreLevel,
)


#
# Generic roles
#
@with_template(LEVEL_TYPES, role="stars")
def level_stars(level, request=None, brackets=None):
    if brackets:
        lbrack, rbrack = brackets
    else:
        lbrack = rbrack = ""
    return {"level": level, "fa_icon": LEVEL_STARS[level], "lbrack": lbrack, "rbrack": rbrack}


@with_template(LEVEL_TYPES, role="description")
def level_description(level, progress=None, **kwargs):
    return {"level": level, "progress": progress, **kwargs}


@with_template(LEVEL_TYPES, role="trophy-image")
def level_trophy_image(level, **kwargs):
    cls = type(level)
    return {"level": level, "img_src": TROPHY_IMG_SRC[cls], "name": TROPHY_NAMES.get(cls, _("Score"))}


#
# Participation progress trophies
#
@with_template(ParticipationProgress, role="statistics")
def participation_progress_statistics(progress, *, classes="margin-y2", **kwargs):
    if isinstance(classes, (tuple, list)):
        classes = " ".join(classes)
    return {"progress": progress, "classes": classes or ""}


@with_template([ConversationProgress, UserProgress], role="statistics")
def user_progress_statistics(progress, *, level, classes="margin-y2", **kwargs):
    if isinstance(classes, (tuple, list)):
        classes = " ".join(classes)
    return {"progress": progress, "classes": classes or "", "kind": LEVEL_KIND[type(level)], "level": level}


#
# Module constants
#
LEVEL_STARS = [None, "far fa-star", "fas fa-star-half-alt", "fas fa-star", "fas fa-trophy"]
TROPHY_NAMES = {
    enums.CommenterLevel: _("Comment score"),
    enums.ConversationLevel: _("Conversation score"),
    enums.HostLevel: _("Conversation score"),
    enums.ProfileLevel: _("Profile score"),
    enums.VoterLevel: _("Participation score"),
    enums.ScoreLevel: _("Total score"),
}
TROPHY_IMG_SRC = {
    # Local
    enums.ConversationLevel: "/img/trophies/host_conversation.svg",
    enums.VoterLevel: "/img/trophies/participate_conversation.svg",
    # Global
    enums.CommenterLevel: "/img/trophies/participation_all.svg",
    enums.HostLevel: "/img/trophies/host_all.svg",
    enums.ProfileLevel: "/img/trophies/profile.svg",
    enums.ScoreLevel: "/img/trophies/total_score.svg",
}
LEVEL_KIND = {
    # Global
    enums.ConversationLevel: "conversation",
    enums.VoterLevel: "voter",
    # Local
    enums.HostLevel: "host",
    enums.CommenterLevel: "comment",
    enums.ProfileLevel: "profile",
    enums.ScoreLevel: "score",
}
