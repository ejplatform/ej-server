from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import VOTE_VALUES, Conversation, Comment


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['title', 'text', 'tags']

    comments_count = forms.IntegerField(initial=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_placeholder('tags', _('Tags, separated by commas'))
        self.set_placeholder('text', _('Type here the question for your research'))
        self.set_placeholder('title', _('A short description about this conversation.'))
        self.fields['text'].widget.attrs.update({
            'onfocus': "this.style.height = (this.scrollHeight) + 'px'",
            'onkeyup': "this.style.height = (this.scrollHeight) + 'px'",
            'class': "Conversation-edit-field",
        })

    def set_placeholder(self, field, value):
        self.fields[field].widget.attrs['placeholder'] = value

    def save_all(self, author, board=None, **kwargs):
        """
        Save model, tags and comments.
        """
        conversation = self.save(commit=False)
        conversation.author = author
        for k, v in kwargs.items():
            setattr(conversation, k, v)
        conversation.save()

        # Save tags on the database
        for tag in self.cleaned_data['tags']:
            conversation.tags.add(tag)

        # Save board
        if board:
            board.add_conversation(conversation)

        # Create comments
        kwargs = {
            'status': Comment.STATUS.approved,
            'check_limits': True,
        }
        n = int(self.data['comments_count'])
        for i in range(n):
            name = f'comment-{i + 1}'
            value = self.data.get(name)
            if value:
                conversation.create_comment(author, value, **kwargs)

        return conversation


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
