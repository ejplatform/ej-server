import pytest

from ej_conversations import create_conversation
from ej_users.models import User
from ej_conversations.forms import CommentForm
from ej_conversations.models import Comment


@pytest.fixture
def user(db):
    user = User.objects.create_user('email@server.com', 'password')
    user.board_name = 'testboard'
    user.save()
    return user


@pytest.fixture
def conversation(db, user):
    return create_conversation(text='test', title='title', author=user, is_promoted=True)


@pytest.fixture
def comment(db, conversation, user):
    return conversation.create_comment(user, 'content', 'approved')


class TestStereotypeForm:
    def test_init(self, conversation):
        CommentForm(conversation=conversation)

    def test_init_without_conversation(self):
        with pytest.raises(KeyError):
            CommentForm()

    def test_valid_data(self, conversation, db, user):
        form = CommentForm({
            'content': "comment content",
        }, conversation=conversation)
        assert form.is_valid()
        comment = form.cleaned_data['content']
        conversation.create_comment(user, comment.content)
        assert comment == "comment content"
        assert comment in conversation.comments

    def test_blank_data(self, conversation):
        form = CommentForm({}, conversation=conversation)
        assert not form.is_valid()
        assert form.errors == {
            'name': ['This field is required.'],
        }

    def test_repetead_stereotype_data(self, conversation, db, user):
        Comment.objects.create(content="Comment", conversation=conversation, owner=user)
        form = CommentForm({
            'content': "Comment",
        }, conversation=conversation)
        assert not form.is_valid()
        assert form.errors == {
            '__all__': ['Stereotype for this conversation with this name already exists.'],
        }
