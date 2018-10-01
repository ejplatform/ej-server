import pytest

from ej_conversations import create_conversation
from ej_users.models import User
from ej_clusters.forms import StereotypeForm
from ej_clusters.models import Stereotype


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
        StereotypeForm(conversation=conversation)

    def test_init_without_conversation(self):
        with pytest.raises(KeyError):
            StereotypeForm()

    def test_valid_data(self, conversation, db, user):
        form = StereotypeForm({
            'name': "Stereotype",
            'description': "description",
        }, conversation=conversation)
        assert form.is_valid()
        stereotype = form.save(commit=False)
        stereotype.owner = user
        stereotype.save()
        assert stereotype.name == "Stereotype"
        assert stereotype.description == "description"

    def test_blank_data(self, conversation):
        form = StereotypeForm({}, conversation=conversation)
        assert not form.is_valid()
        assert form.errors == {
            'name': ['This field is required.'],
        }

    def test_edit_existing_stereotype(self, conversation, db, user):
        instance = Stereotype.objects.create(name="Stereotype1", conversation=conversation, owner=user)
        form = StereotypeForm({
            'name': "Stereotype1",
            'description': "description",
        }, conversation=conversation, instance=instance)
        assert form.is_valid()

    def test_repetead_stereotype_data(self, conversation, db, user):
        Stereotype.objects.create(name="Stereotype1", conversation=conversation, owner=user)
        form = StereotypeForm({
            'name': "Stereotype1",
            'description': "description",
        }, conversation=conversation)
        assert not form.is_valid()
        assert form.errors == {
            '__all__': ['Stereotype for this conversation with this name already exists.'],
        }
