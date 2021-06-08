from django.utils.translation import ugettext_lazy as _
from boogie import models
from boogie.rest import rest_api


@rest_api(["conversation", "domain"])
class RasaConversation(models.Model):
    """
    Allows correlation between a conversation and an instance of rasa
    running on an external website
    """

    conversation = models.ForeignKey("Conversation", on_delete=models.CASCADE, related_name="rasa_conversations")
    domain = models.URLField(
        _("Domain"),
        max_length=255,
        help_text=_("The domain that the rasa bot webchat is hosted."),)

    class Meta:
        unique_together = (('conversation', 'domain'),)
        ordering = ['-id']


class ConversationComponent:
    """
    ConversationComponent controls the steps to generate the script and css to
    configure the EJ opinion web component;
    """

    AUTH_TYPE_CHOICES = (
        ("register", _("Register using name/email")),
        ("mautic", _("Mautic")),
        ("analytics", _("Analytics")),
    )

    AUTH_TOOLTIP_TEXTS = {
        "register": _("User will use EJ platform interface, creating an account using personal data"),
        "mautic": _("Uses a mautic campaign "),
        "analytics": _("Uses analytics cookies allowing you to cross vote data with user browser data.")
    }

    THEME_CHOICES = (
        ("default", _("Default")),
        ("votorantim", _("Votorantim")),
        ("icd", _("ICD")),
    )

    THEME_PALETTES = {
        "default": ["#1D1088", "#F8127E"],
        "votorantim": ["#04082D", "#F14236"],
        "icd": ["#005BAA", "#F5821F"]
    }

    def __init__(self, form):
        self.form = form

    def _form_is_invalid(self):
        return not self.form.is_valid() or (not self.form.cleaned_data["theme"] and not self.form.cleaned_data["authentication_type"])

    def get_props(self):
        if self._form_is_invalid():
            return "theme= authenticate-with=register"

        result = ""
        if self.form.cleaned_data["theme"] != "default":
            result = result + f"theme={self.form.cleaned_data['theme']}"
        if self.form.cleaned_data["authentication_type"]:
            result = result + f" authenticate-with={self.form.cleaned_data['authentication_type']}"
        return result


class MailingTool:
    MAILING_TOOL_CHOICES = (
        ("mautic", _("Mautic")),
        ("mailchimp", _("MailChimp")),
    )

    MAILING_TOOLTIP_TEXTS = {
        "mailchimp": _("Mailchimp campaign"),
        "mautic": _("Uses a mautic campaign "),
    }
