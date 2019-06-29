from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import Blob

from .models import UserProgress, ParticipationProgress, ConversationProgress

trophy_template = get_template("roles/ej/trophy.jinja2")


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


def participate_conversation_trophy(progress: ParticipationProgress):
    level = progress.voter_level
    return trophy(
        "participate_conversation",
        progress.conversation.title,
        level=level,
        href=progress.conversation.get_absolute_url(),
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
