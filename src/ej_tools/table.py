from django.utils.translation import ugettext_lazy as _


class Tools:
    def __init__(self, conversation):
        self.conversation = conversation

    def list(self):
        return [
            {
                "integration": _("Mailing campaign"),
                "description": _(
                    "Generates a html template of this conversation, for mailing marketing campaigns."
                ),
                "link": self.conversation.url("conversation-tools:mailing"),
                "about": "/docs/?page=user-docs/tools-mail-template.html",
            },
            {
                "integration": _("Opinion component"),
                "description": _(
                    "Conduct opinion collections without your audience having to access EJ directly. Allows you to vote, comment and view groups directly on html pages, without impacting the experience of those who already access their networks and platforms."
                ),
                "link": self.conversation.url("conversation-tools:opinion-component"),
                "about": "/docs/?page=user-docs/tools-opinion-component.html",
            },
            {
                "integration": _("Chatbot"),
                "description": _(
                    "Collect opinions using EJ's chatbot, also known as Duda. Allows, via webchat, telegram and whatsapp to vote and comment on EJ's conversations."
                ),
                "description_chatbots": _(
                    "Collect opinions using EJ's chatbot, also known as Duda. You are going to be able to do collects from whatsapp, telegram or through webchat. Select one of the options to conduct the collect configuration"
                ),
                "description_whatsapp": _(
                    "Whatsapp user will interact with the bot in the private chat. Use Twilio as a broker for connection."
                ),
                "description_telegram": _(
                    "Telegram user will interact with the bot in the private chat. Use telegram API for connection."
                ),
                "description_webchat": _(
                    "Integrate this conversation with a web client, called a webchat. Create a chat on your website page."
                ),
                "link": self.conversation.url("conversation-tools:chatbot"),
                "about": "/docs/?page=user-docs/tools-chatbot.html",
            },
            {
                "integration": _("Mautic"),
                "description": _(
                    "Integrate this conversation with the Mautic platform API, allowing users who participate in this conversation to be automatically synchronized with Mautic's contact base."
                ),
                "link": self.conversation.url("conversation-tools:mautic"),
                "about": "/docs/?page=user-docs/tools-mautic.html",
            },
        ]

    def get(self, name):
        tools = self.list()
        selected_tool = {}
        for tool in tools:
            if tool["integration"] == name:
                selected_tool = tool
                break
        if not selected_tool:
            raise Exception("tool not found")
        return selected_tool
