import pytest

from ej_conversations import mommy_recipes as conversations


@pytest.fixture
def conversation(db):
    """
    Conversation with votes, comments and clusters.
    """
    conversation = conversations.conversation.make()
    return conversation


class TestClusterization:
    def test_inject_clusters_related_manager_on_conversation(self, conversation):
        assert hasattr(conversation.clusterization, 'clusters')
        assert hasattr(conversation, 'clusters')


class TestStereotype:
    def test_inject_stereotype_related_manager_on_conversation(self, conversation):
        assert not conversation.stereotypes
        assert hasattr(conversation, 'stereotypes')
