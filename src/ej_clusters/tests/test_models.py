import pytest

from ej_conversations import mommy_recipes as conversations


@pytest.fixture(scope='class')
def conversation(db):
    """
    Conversation with votes, comments and clusters.
    """
    conversation = conversations.conversation()
    return conversation


class TestClusterization:
    def test_inject_clusters_related_manager_on_conversation(self, conversation):
        conversation.clusters
