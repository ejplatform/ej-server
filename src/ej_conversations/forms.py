from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from sidekick import identity

from ej.forms import EjModelForm, EjUserForm
from .models import Conversation, Comment


class CommentForm(EjModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        help_texts = {"content": None}

    def __init__(self, *args, conversation, **kwargs):
        self.conversation = conversation
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["placeholder"] = _("Give your opinion here")
        self.fields["content"].widget.attrs["title"] = _("Suggest a new comment")

    def clean(self):
        super().clean()
        content = (self.cleaned_data.get("content") or "").strip()
        if content:
            comment_exists = Comment.objects.filter(
                content=content, conversation=self.conversation
            ).exists()
            if comment_exists:
                msg = _("You already submitted this comment.")
                raise ValidationError({"content": msg})
            self.cleaned_data["content"] = content
        return self.cleaned_data


class ConversationForm(EjModelForm):
    """
    Form used to create and edit conversations.
    """

    comments_count = forms.IntegerField(initial=3, required=False)
    tags = forms.CharField(label=_("Tags"), help_text=_("Tags, separated by commas."), required=False)

    class Meta:
        model = Conversation
        fields = ["title", "text", "is_promoted"]  # "is_hidden"
        help_texts = {
            "is_promoted": _("Place conversation in the main /conversations/ URL."),
            "is_hidden": _("Mark to make the conversation invisible."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("tags", "text"):
            self.set_placeholder(field, self[field].help_text)
        if self.instance and self.instance.id is not None:
            self.fields["tags"].initial = ", ".join(self.instance.tags.values_list("name", flat=True))

    def set_placeholder(self, field, value):
        self.fields[field].widget.attrs["placeholder"] = value

    def save(self, commit=True, board=None, **kwargs):
        if not board:
            raise ValidationError("Board field should not be empty")
        conversation = super().save(commit=False)
        conversation.board = board

        for k, v in kwargs.items():
            setattr(conversation, k, v)

        if commit:
            conversation.save()

            # Save tags on the database
            tags = self.cleaned_data["tags"].split(",")
            tags = map(lambda x: x.strip(",."), tags)
            conversation.tags.set(*filter(identity, tags), clear=True)

        return conversation

    def save_comments(self, author, check_limits=True, status=Comment.STATUS.approved, **kwargs):
        """
        Save model, tags and comments.
        """
        conversation = self.save(author=author, **kwargs)

        # Create comments
        kwargs = {"status": status, "check_limits": check_limits}
        n = int(self.data["comments_count"])
        for i in range(n):
            name = f"comment-{i + 1}"
            value = self.data.get(name)
            if value:
                try:
                    conversation.create_comment(author, value, **kwargs)
                # Duplicate or empty comment...
                except ValidationError:
                    pass
        return conversation
