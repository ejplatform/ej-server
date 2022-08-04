from logging import getLogger
from abc import ABC, abstractmethod
from constance import config
from django.utils.translation import gettext_lazy as _
from ej_tools.tools import *

log = getLogger("ej")


class Signature(ABC):
    """
    Abstract class that defines generic actions to be performed by its signature subclasses.
    """

    def __init__(self, user):
        self.user = user

    def can_add_conversation(self) -> bool:
        if self.user.is_superuser:
            return True

        user_conversations_count = self.user.conversations.count()
        if user_conversations_count < self.get_conversation_limit():
            return True
        else:
            return False

    def get_tool(self, tool_name, conversation):
        """Returns a tool that is available on user signature

        :tool_name: Tool Name
        :conversation: Conversation instance
        :returns: Tool instance
        """
        tools = self.get_conversation_tools(conversation)
        return Tools.get(tool_name, tools)

    def can_vote(self) -> bool:
        if self.user.is_superuser:
            return True

        user_vote_count = self.user.votes.count()
        if user_vote_count < self.get_vote_limit():
            return True
        else:
            return False

    @abstractmethod
    def get_conversation_limit(self) -> int:
        pass

    @abstractmethod
    def get_vote_limit(self) -> int:
        pass

    @abstractmethod
    def get_conversation_tools(self, conversation) -> list:
        pass


class ListenToCommunity(Signature):
    def __init__(self, user):
        Signature.__init__(self, user)
        self.available_tools = []

    def get_conversation_limit(self) -> int:
        return config.EJ_LISTEN_TO_COMMUNITY_SIGNATURE_CONVERSATIONS_LIMIT

    def get_vote_limit(self) -> int:
        return config.EJ_LISTEN_TO_COMMUNITY_SIGNATURE_VOTE_LIMIT

    def get_conversation_tools(self, conversation) -> list:
        """
        Returns the list of tools available for ListenToCommunity signature.
        :arg1: conversation
        :returns: list of tools
        """
        exclude = []
        if not self.user.is_superuser:
            exclude.append("whatsapp")

        return [
            MailingTool(conversation),
            OpinionComponentTool(conversation),
            BotsTool(conversation, exclude=exclude),
            MauticTool(conversation, is_active=False),
            RocketChat(conversation, is_active=False),
        ]


class ListenToCity(Signature):
    def __init__(self, user):
        Signature.__init__(self, user)
        self.available_tools = []

    def get_conversation_limit(self) -> int:
        return config.EJ_LISTEN_TO_CITY_SIGNATURE_CONVERSATIONS_LIMIT

    def get_vote_limit(self) -> int:
        return config.EJ_LISTEN_TO_CITY_SIGNATURE_VOTE_LIMIT

    def get_conversation_tools(self, conversation) -> list:
        """
        Returns the list of tools available for ListenToCommunity signature.
        :arg1: conversation
        :returns: list of tools
        """
        return [
            MailingTool(conversation),
            OpinionComponentTool(conversation),
            BotsTool(conversation),
            MauticTool(conversation),
            RocketChat(conversation),
        ]


class ListenToCityYearly(Signature):
    def __init__(self, user):
        Signature.__init__(self, user)
        self.available_tools = []

    def get_conversation_limit(self) -> int:
        return config.EJ_LISTEN_TO_CITY_YEARLY_SIGNATURE_CONVERSATIONS_LIMIT

    def get_vote_limit(self) -> int:
        return config.EJ_LISTEN_TO_CITY_YEARLY_SIGNATURE_VOTE_LIMIT

    def get_conversation_tools(self, conversation) -> list:
        """
        Returns the list of tools available for ListenToCommunity signature.
        :arg1: conversation
        :returns: list of tools
        """

        whatsapp = []
        if not self.user.is_superuser:
            whatsapp.append("whatsapp")

        return [
            MailingTool(conversation),
            OpinionComponentTool(conversation),
            BotsTool(conversation, exclude=whatsapp),
            MauticTool(conversation, is_active=False),
            RocketChat(conversation, is_active=False),
        ]


class SignatureFactory:
    """
    Instantiates signature subclasses
    Usage:

    signature = SignatureFactory.get_user_signature(request.user)
    signature.<method-from-class>()
    """

    LISTEN_TO_COMMUNITY = "listen_to_community"
    LISTEN_TO_CITY = "listen_to_city"
    LISTEN_TO_CITY_YEARLY = "listen_to_city_yearly"

    signatures = {
        LISTEN_TO_COMMUNITY: ListenToCommunity,
        LISTEN_TO_CITY: ListenToCity,
        LISTEN_TO_CITY_YEARLY: ListenToCityYearly,
    }

    @staticmethod
    def get_user_signature(user) -> Signature:
        signature_klass = SignatureFactory.signatures.get(user.signature)
        try:
            return signature_klass(user)
        except:
            return None

    @staticmethod
    def plans():
        return [
            (SignatureFactory.LISTEN_TO_COMMUNITY, _("Listen to community")),
            (SignatureFactory.LISTEN_TO_CITY, _("Listen to city")),
            (SignatureFactory.LISTEN_TO_CITY_YEARLY, _("Listen to city yearly")),
        ]
