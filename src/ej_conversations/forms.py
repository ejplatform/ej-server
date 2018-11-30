from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Conversation, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, conversation, **kwargs):
        self.conversation = conversation
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['placeholder'] = _('Give your opinion here')

    def clean(self):
        super().clean()
        content = self.cleaned_data.get('content')
        comment_exists = Comment.objects.filter(content=content, conversation=self.conversation).exists()
        if comment_exists:
            msg = _("It seems that you created repeated comments. Please verify if there aren't any equal comments")
            self._errors['content'] = self.error_class([msg])
            del self.cleaned_data['content']
            raise ValidationError(msg)
        return self.cleaned_data


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['title', 'text', 'tags']

    comments_count = forms.IntegerField(initial=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_placeholder('tags', _('Tags, separated by commas'))
        self.set_placeholder('text', _('Type here the question for your research'))
        self.set_placeholder('title', _('Permanent link.'))
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
        self.save_m2m()

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
