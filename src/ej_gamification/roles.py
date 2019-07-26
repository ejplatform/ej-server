from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import Blob

from ej.roles import with_template
from . import enums
from .models import UserProgress, ParticipationProgress, ConversationProgress

trophy_template = get_template("roles/ej/trophy.jinja2")
LEVEL_STARS = [None, "far fa-star", "fas fa-star-half-alt", "fas fa-star", "fas fa-trophy"]
TROPHY_NAMES = {
    enums.CommenterLevel: _("Comment score"),
    enums.ConversationLevel: _("Conversation score"),
    enums.HostLevel: _("Conversation score"),
    enums.ProfileLevel: _("Profile score"),
    enums.VoterLevel: _("Participation score"),
}
TROPHY_IMG_SRC = {
    # Local
    enums.ConversationLevel: "/img/trophies/host_conversation.svg",
    enums.VoterLevel: "/img/trophies/participate_conversation.svg",
    # Global
    enums.CommenterLevel: "/img/trophies/participation_all.svg",
    enums.HostLevel: "/img/trophies/host_all.svg",
    enums.ProfileLevel: "/img/trophies/profile.svg",
}
LEVEL_TYPES = tuple(TROPHY_IMG_SRC)


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
def level_description(level, request=None, progress=None):
    return {"level": level, "progress": progress}


@with_template(LEVEL_TYPES, role="trophy-image")
def level_trophy_image(level, request=None):
    cls = type(level)
    return {"level": level, "img_src": TROPHY_IMG_SRC[cls], "name": TROPHY_NAMES.get(cls, _("Score"))}


#
# Participation progress trophies
#
@with_template(ParticipationProgress, role="trophy")
def participation_progress_trophy(progress: ParticipationProgress, request=None):
    level = progress.voter_level
    return {
        "progress": progress,
        "conversation": progress.conversation,
        "user": progress.user,
        "href": progress.conversation.get_absolute_url(),
        "description": level.achieve_next_level_msg(progress),
        "img_src": "/img/trophies/participate_conversation.svg",
        "img_description": "fdfoss",
        "details": (),
    }


@with_template(ParticipationProgress, role="statistics")
def participation_progress_statistics(progress: ParticipationProgress, request=None, classes=None):
    if isinstance(classes, (tuple, list)):
        classes = " ".join(classes)
    return {"progress": progress, "classes": classes}


#
# Other trophies
#
def profile_trophy(progress: UserProgress):
    level = progress.profile_level
    return trophy(
        "profile",
        _("Profile"),
        level=level,
        href=reverse("profile:detail"),
        msg=level.achieve_next_level_msg(progress),
    )


def host_trophy(progress: UserProgress):
    level = progress.host_level
    return trophy(
        "host_all",
        _("Conversations"),
        level=level,
        href=reverse("profile:contributions") + "#contribution-conversations",
        msg=level.achieve_next_level_msg(progress),
    )


def participation_trophy(progress: UserProgress):
    level = progress.commenter_level
    return trophy(
        "participation_all",
        _("Participation"),
        level=level,
        href=reverse("profile:contributions") + "#contribution-comments",
        msg=level.achieve_next_level_msg(progress),
    )


def host_conversation_trophy(progress: ConversationProgress):
    level = progress.conversation_level
    return trophy(
        "host_conversation",
        progress.conversation.title,
        level=level,
        href=progress.conversation.get_absolute_url(),
        msg=level.achieve_next_level_msg(progress),
    )


def trophy(icon, name, level=0, href=None, msg=""):
    """
    Render a trophy
    """
    banner = None
    img_classes = []
    if level == 0:
        img_classes.append("opacity-3")
    elif level == 1:
        img_classes.append("opacity-4")
    elif level == 2:
        banner = "star"
    elif level == 2:
        banner = "shield-alt"
    elif level == 4:
        banner = "crown"

    return Blob(
        trophy_template.render(
            {
                "icon_name": icon,
                "name": name,
                "level": int(level),
                "href": href,
                "msg": msg,
                "img_classes": " ".join(img_classes),
                "banner": banner,
            }
        )
    )
