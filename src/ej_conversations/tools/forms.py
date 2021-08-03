from django import forms
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from ej_boards.forms import PaletteWidget
from ej_conversations.models import Comment
from ej.forms import EjModelForm
from .models import RasaConversation, ConversationComponent, MailingTool, ConversationMautic


class CustomChoiceWidget(forms.RadioSelect):
    template_name = "ej_conversations_tools/includes/custom-select.jinja2"
    renderer = get_template(template_name)

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return self.renderer.render(context)


class CustomTemplateChoiceWidget(forms.RadioSelect):
    template_name = "ej_conversations_tools/includes/template-type.jinja2"
    renderer = get_template(template_name)

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return self.renderer.render(context)


class ConversationComponentForm(forms.Form):
    authentication_type = forms.ChoiceField(
        label=_("Authentication Type"),
        choices=ConversationComponent.AUTH_TYPE_CHOICES,
        required=False,
        widget=CustomChoiceWidget(attrs=ConversationComponent.AUTH_TOOLTIP_TEXTS),
    )
    theme = forms.ChoiceField(
        label=_("Theme"), choices=ConversationComponent.THEME_CHOICES, required=False, widget=PaletteWidget
    )


class MailingToolForm(forms.Form):
    template_type = forms.ChoiceField(
        label=_("Template type"),
        choices=MailingTool.MAILING_TOOL_CHOICES,
        required=False,
        widget=CustomTemplateChoiceWidget(attrs=MailingTool.MAILING_TOOLTIP_TEXTS),
    )
    theme = forms.ChoiceField(
        label=_("Theme"), choices=ConversationComponent.THEME_CHOICES, required=False, widget=PaletteWidget
    )
    is_custom_domain = forms.BooleanField(
        required=False, label=_("Redirect user to a custom domain (optional)")
    )
    custom_title = forms.CharField(
        required=False, label=_("Adds a custom title to the template (optional).")
    )
    custom_comment = forms.ModelChoiceField(
        queryset=None, required=False, label=_("selects a specific comment for user to vote (optional).")
    )

    def __init__(self, *args, **kwargs):
        conversation_id = kwargs.pop("conversation_id")
        super(MailingToolForm, self).__init__(*args, **kwargs)
        self.fields["custom_comment"].queryset = Comment.objects.filter(conversation=conversation_id)


class RasaConversationForm(EjModelForm):
    class Meta:
        model = RasaConversation
        fields = ["conversation", "domain"]
        help_texts = {"conversation": None, "domain": None}


class MauticConversationForm(EjModelForm):
    class Meta:
        model = ConversationMautic
        fields = ["user_name", "url", "conversation", "password"]
