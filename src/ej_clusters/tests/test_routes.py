import pytest

from ej.testing import UrlTester
from ej_clusters import routes
from ej_clusters.models import Stereotype, StereotypeVote, Cluster
from ej_clusters.mommy_recipes import ClusterRecipes
from ej_conversations import Choice
from ej_conversations.models import Conversation
from ej_users.models import User


class TestRoutes(UrlTester, ClusterRecipes):
    owner_urls = [
        '/conversations/conversation/stereotypes/add/',
        '/conversations/conversation/stereotypes/',
        # '/conversations/conversation/stereotypes/1/edit'
    ]

    @pytest.fixture
    def data(self, conversation, author_db, stereotype):
        conversation.author = author_db
        conversation.save()
        stereotype.owner = author_db
        stereotype.save()
        return {
            'conversation': conversation.__dict__,
            'author': author_db.__dict__,
            'stereotype': stereotype.__dict__,
            'clusterization': conversation.get_clusterization(),
        }


@pytest.fixture
def user(db):
    return User.objects.create_user('name@server.com', '1234', name='name')


@pytest.fixture
def conversation(user):
    return Conversation.objects.create(title='Title', author=user)


@pytest.fixture
def comment(conversation, user):
    return conversation.create_comment(user, 'comment', 'approved')


@pytest.fixture
def stereotype(user, comment):
    stereotype = Stereotype.objects.create(name='stereo', owner=user)
    StereotypeVote.objects.create(author=stereotype, choice=Choice.SKIP, comment=comment)
    return stereotype


class TestClusterRoutes(ClusterRecipes):
    def test_user_conversation_clusters(self, rf, cluster_db):
        request = rf.get('')
        request.user = cluster_db.clusterization.owner
        response = routes.list_cluster(request)
        assert response['clusters'].first() == cluster_db

    def test_conversation_clusters(self, clusterization_db):
        cluster = Cluster.objects.create(clusterization=clusterization_db, name='cluster')
        response = routes.index(clusterization_db.conversation)
        assert response['clusters'].first() == cluster

    def test_clusters_detail(self, clusterization_db):
        cluster = Cluster.objects.create(clusterization=clusterization_db, name='cluster')
        response = routes.detail(clusterization_db.conversation, cluster)
        assert response['cluster'] == cluster
        assert response['conversation'] == clusterization_db.conversation

    def test_conversation_clusterize(self, clusterization_db, stereotype_db):
        cluster = Cluster.objects.create(clusterization=clusterization_db, name='cluster')
        cluster.stereotypes.set([stereotype_db])
        response = routes.clusterize(clusterization_db.conversation)
        assert response['content_title'] == 'Force clusterization'
        assert response['clusterization'] == clusterization_db


class TestStereotypeRoutes:
    def test_create_stereotype(self, rf, comment, user):
        data = {'name': 'something',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-MIN_NUM_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                'form-0-comment': comment.id,
                'form-0-choice': '0',
                'form-0-id': ''}
        request = rf.post('', data)
        request.user = user
        comment.conversation.get_clusterization()
        response = routes.create_stereotype(request, comment.conversation)
        assert response.status_code == 302
        assert response.url == "/conversations/title/stereotypes/"

    def test_create_invalid_stereotype(self, rf, comment):
        data = {'name': '',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-MIN_NUM_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                'form-0-comment': '',
                'form-0-choice': 0,
                'form-0-id': ''}
        request = rf.post('', data)
        request.user = comment.author
        comment.conversation.get_clusterization()
        response = routes.create_stereotype(request, comment.conversation)
        assert not response['stereotype_form'].is_valid()

    def test_edit_stereotype(self, rf, user, conversation, stereotype, comment):
        data = {'name': 'stereo',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-MIN_NUM_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                'form-0-comment': comment.id,
                'form-0-choice': '1',
                'form-0-id': ''}
        request = rf.post('', data)
        request.user = user
        response = routes.edit_stereotype(request, conversation, stereotype)
        assert response.status_code == 302
        assert response.url == "/conversations/title/stereotypes/"

    def test_edit_invalid_stereotype(self, rf, user, stereotype, conversation):
        data = {'name': 'stereo',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-MIN_NUM_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                'form-0-comment': '30',
                'form-0-choice': '1',
                'form-0-id': ''}
        request = rf.post('', data)
        request.user = user
        response = routes.edit_stereotype(request, conversation, stereotype)
        assert not response['votes_form'].is_valid()

    def test_edit_get_stereotype(self, rf, user, stereotype, conversation):
        request = rf.get('')
        request.user = user
        response = routes.edit_stereotype(request, conversation, stereotype)
        assert response['stereotype_form']
        assert response['votes_form']

    def test_stereotype_vote_post(self, rf, user, conversation, stereotype, comment):
        new_comment = conversation.create_comment(user, 'new comment', 'approved')
        data = {'choice-' + str(new_comment.id): ['AGREE']}
        request = rf.post('', data)
        request.user = user
        response = routes.stereotype_vote(request, conversation, stereotype)
        assert response['conversation'] == conversation
        assert response['stereotype'] == stereotype

    def test_stereotype_vote_get(self, rf, user, conversation, stereotype):
        request = rf.get('')
        request.user = user
        response = routes.stereotype_vote(request, conversation, stereotype)
        assert response['conversation'] == conversation
        assert response['stereotype'] == stereotype
