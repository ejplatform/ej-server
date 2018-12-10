from django import forms
from django.utils.translation import ugettext_lazy as _


class TalkToUsForm(forms.Form):
    subject = forms.CharField(
        label=_('Subject'),
    )
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea,
    )
