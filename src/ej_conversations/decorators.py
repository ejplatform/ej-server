from ej_tools.tools import BotsTool
from ej_users.models import SignatureFactory
from ej_conversations.models.vote import VoteChannels
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


TOOLS_CHANNEL = {
    "socketio": (_("Opinion Bots"), "webchat"),
    "telegram": (_("Opinion Bots"), "telegram"),
    "twilio": (_("Opinion Bots"), "whatsapp"),
    "opinion_component": (_("Opinion component"),),
    "rocketchat": (_("Rocket.Chat"),),
    "unknown": (),
}


def bot_tool_is_active(bots_tool, tool_name):
    """
    checks if a certain type of bot (webchat, telegram, whatsapp) is active.
    """
    tool = getattr(bots_tool, tool_name)
    return tool.is_active


def author_can_receive_tool_vote(func):
    """
    Checks if the conversation author is allowed to receive votes from a given tool.

    If the author does not have permission, a 403 error is raised.
    """

    def wrapper_func(self, request, vote):
        if vote.channel == VoteChannels.UNKNOWN:
            raise PermissionDenied(
                {"message": "conversation author can not receive votes from an unknown tool"}
            )

        try:
            conversation = vote.comment.conversation
            author_signature = SignatureFactory.get_user_signature(conversation.author)
            tool_channel = TOOLS_CHANNEL[vote.channel]
            tool = author_signature.get_tool(tool_channel[0], conversation)
        except Exception:
            raise PermissionDenied({"message": f"{vote.channel} tool was not found"})

        if not tool.is_active:
            raise PermissionDenied(
                {"message": f"{vote.channel} is not available on conversation author signature"}
            )
        if type(tool) == BotsTool and not bot_tool_is_active(tool, tool_channel[1]):
            raise PermissionDenied(
                {"message": f"{vote.channel} is not available on conversation author signature"}
            )

        return func(self, request, vote)

    return wrapper_func
