from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from sidekick import identity

from ej.forms import EjModelForm
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


class ModerationForm(EjModelForm):
    """
    Form used during moderation of a conversation's comments.
    """

    class Meta:
        model = Comment
        fields = ['status', 'rejection_reason_option', 'rejection_reason']
        help_texts = {'rejection_reason': None}

    def _clean_fields(self):
        self.data = self.data.copy()
        if 'reject_id' in self.data:
            comment_id = int(self.data['reject_id'])
            self.instance = Comment.objects.get(id=comment_id)
            self.data['status'] = Comment.STATUS.rejected
        elif 'approve_id' in self.data:
            comment_id = int(self.data['approve_id'])
            self.instance = Comment.objects.get(id=comment_id)
            self.data['status'] = Comment.STATUS.approved
        else:
            raise ValueError('invalid POST data')
        super()._clean_fields()


class ConversationForm(EjModelForm):
    """
    Form used to create and edit conversations.
    """
    comments_count = forms.IntegerField(initial=3, required=False)
    tags = forms.CharField(label=_('Tags'), help_text=_('Tags, separated by commas.'))

    class Meta:
        model = Conversation
        fields = ['title', 'text', 'is_promoted', 'is_hidden']
        help_texts = {'is_promoted': _('Place conversation in the main /conversations/ URL.'),
                      'is_hidden': _('Mark to make the conversation invisible.')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('tags', 'text'):
            self.set_placeholder(field, self[field].help_text)
        if self.instance and not self.instance.id is None:
            self.fields['tags'].initial = ', '.join(self.instance.tags.values_list('name', flat=True))

    def set_placeholder(self, field, value):
        self.fields[field].widget.attrs['placeholder'] = value

    def save(self, commit=True, board=None, **kwargs):
        conversation = super().save(commit=False)
        for k, v in kwargs.items():
            setattr(conversation, k, v)

        if commit:
            conversation.save()

            # Save tags on the database
            tags = self.cleaned_data['tags'].split(',')
            tags = map(lambda x: x.strip(',.'), tags)
            conversation.tags.set(*filter(identity, tags), clear=True)

            # Save board
            if board:
                board.add_conversation(conversation)

        return conversation

    def save_comments(self, author, check_limits=True,
                      status=Comment.STATUS.approved, **kwargs):
        """
        Save model, tags and comments.
        """
        conversation = self.save(author=author, **kwargs)

        # Create comments
        kwargs = {
            'status': status,
            'check_limits': check_limits,
        }
        n = int(self.data['comments_count'])
        for i in range(n):
            name = f'comment-{i + 1}'
            value = self.data.get(name)
            if value:
                conversation.create_comment(author, value, **kwargs)

        return conversation
