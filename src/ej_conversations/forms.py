from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .models import VOTE_VALUES, Conversation, Comment
from .validators import validate_board_name


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['title', 'text', 'tags']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class VoteForm(forms.Form):
    value = forms.IntegerField(required=False)
    action = forms.ChoiceField(choices=['agree', 'disagree', 'skip'], required=False)

    def get_value(self):
        if not self.is_valid():
            raise ValidationError(self.errors)

        value = self.cleaned_data["choice"]
        if value is not None:
            return value

        action = self.cleaned_data['action']
        if action:
            return VOTE_VALUES[action]
        return 0


class FirstConversationForm(ConversationForm):
    board_name = forms.CharField(
        label=_('Board name'),
        required=True,
        max_length=140,
        help_text=_('The name of your conversation board.'),
        validators=[validate_board_name]
    )

    def clean_board_name(self):
        board_name = self.cleaned_data['board_name'].lower()
        aux = ' '.join(board_name.split())
        return aux.replace(' ', '_')