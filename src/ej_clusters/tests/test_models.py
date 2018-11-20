import pytest

from ej.testing import EjRecipes
from ej_conversations import mommy_recipes as conversations
from ej_conversations.models import Conversation
from ej_clusters.models import Cluster


@pytest.fixture
def conversation(db):
    """
    Conversation with votes, comments and clusters.
    """
    conversation = conversations.conversation.make()
    return conversation


@pytest.fixture
def author(db):
    return EjRecipes.author.make()


class TestClusterization():
    def test_inject_clusters_related_manager_on_conversation(self, conversation):
        assert hasattr(conversation.clusterization, 'clusters')
        assert hasattr(conversation, 'clusters')

    def test_clusterization_str_method(self, db, author):
        conversation = Conversation.objects.create(author=author, title='title')
        clusterization = conversation.clusterization
        assert f'{conversation} (0 clusters)' == str(clusterization)
        assert '/conversations/title/clusters/' == clusterization.get_absolute_url()


class TestCluster():
    def test_cluster_str_method(self, db, author):
        conversation = Conversation.objects.create(author=author, title='newtitle')
        cluster = Cluster.objects.create(clusterization=conversation.clusterization, name='cluster')
        cluster_id = str(cluster.pk)
        assert 'cluster ("newtitle" conversation)' == str(cluster)
        assert '/conversations/newtitle/clusters/' + cluster_id + '/' == cluster.get_absolute_url()


class TestStereotype:
    def test_inject_stereotype_related_manager_on_conversation(self, conversation):
        assert not conversation.stereotypes.all()
