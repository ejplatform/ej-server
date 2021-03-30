from django import forms
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from ej_boards.forms import PaletteWidget
from ej.forms import EjModelForm
from .models import RasaConversation, ConversationComponent, MailingTool


class CustomChoiceWidget(forms.RadioSelect):
    template_name = "ej_conversations_tools/includes/custom-select.jinja2"
    renderer = get_template(template_name)

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return self.renderer.render(context)


class ConversationComponentForm(forms.Form):
    authentication_type = forms.ChoiceField(
        label=_("Authentication Type"), choices=ConversationComponent.AUTH_TYPE_CHOICES,
        required=False, widget=CustomChoiceWidget(attrs=ConversationComponent.AUTH_TOOLTIP_TEXTS)
    )
    theme = forms.ChoiceField(
        label=_("Theme"), choices=ConversationComponent.THEME_CHOICES,
        required=False, widget=PaletteWidget
    )

class MailingToolForm(forms.Form):
    mailing_tool_type = forms.ChoiceField(
        label=_("Select a marketing tool to generate a compatible template"),
        choices=MailingTool.MAILING_TOOL_CHOICES, required=False,
        widget=CustomChoiceWidget(attrs=MailingTool.MAILING_TOOLTIP_TEXTS)
    )
    theme = forms.ChoiceField(
        label=_("Theme"), choices=ConversationComponent.THEME_CHOICES,
        required=False, widget=PaletteWidget
    )
    is_custom_domain = forms.BooleanField(
        required=False,
        label=_("Redirect user to a custom domain")
    )

class RasaConversationForm(EjModelForm):
    class Meta:
        model = RasaConversation
        fields = ["conversation", "domain"]
        help_texts = {"conversation": None, "domain": None}

    def __init__(self, *args, conversation, **kwargs):
        kwargs.update(initial={
            'conversation': conversation
        })
        super(RasaConversationForm, self).__init__(*args, **kwargs)
