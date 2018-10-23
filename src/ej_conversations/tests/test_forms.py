import pytest

from ej_conversations.forms import CommentForm
from ej_conversations.models import Comment


class TestCommentForm:
    def test_init(self, conversation):
        CommentForm(conversation=conversation)

    def test_init_without_conversation(self):
        with pytest.raises(TypeError):
            CommentForm()

    def test_valid_data(self, conversation, db, user):
        form = CommentForm({
            'content': "comment content",
        }, conversation=conversation)
        assert form.is_valid()
        comment = form.cleaned_data['content']
        conversation.create_comment(user, comment)
        assert comment == "comment content"

    def test_blank_data(self, conversation):
        form = CommentForm({}, conversation=conversation)
        assert not form.is_valid()
        assert form.errors == {
            'content': ['This field is required.'],
        }

    def test_repetead_comment_data(self, conversation, db, user):
        Comment.objects.create(content="Comment", conversation=conversation, author=user)
        form = CommentForm({
            'content': "Comment",
        }, conversation=conversation)
        assert not form.is_valid()
        print(form.errors['content'])
        assert form.errors['content'] == [
            'It seems that you created repeated comments. Please verify if there aren\'t any equal comments']
