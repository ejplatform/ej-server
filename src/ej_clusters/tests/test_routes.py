import pytest
from django.http import Http404

from ej.testing import UrlTester
from ej_clusters.models import Stereotype, StereotypeVote, Cluster
from ej_clusters.mommy_recipes import ClustersRecipes
from ej_clusters import routes
from ej_conversations.models import Conversation, Choice
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_users.models import User


class TestRoutes(UrlTester, ConversationRecipes, ClustersRecipes):
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
        stereotype.conversation = conversation
        stereotype.save()
        return {
            'conversation': conversation.__dict__,
            'author': author_db.__dict__,
            'stereotype': stereotype.__dict__,
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
def stereotype(conversation, user, comment):
    stereotype = Stereotype.objects.create(name='stereo', conversation=conversation, owner=user)
    StereotypeVote.objects.create(author=stereotype, choice=Choice.SKIP, comment=comment)
    return stereotype


class TestClusterRoutes:
    def test_user_conversation_clusters(self, rf, conversation, user):
        cluster = Cluster.objects.create(clusterization=conversation.clusterization, name='cluster')
        request = rf.get('')
        request.user = user
        response = routes.list_cluster(request)
        assert response['clusters'].first() == cluster

    def test_conversation_clusters(self, conversation):
        cluster = Cluster.objects.create(clusterization=conversation.clusterization, name='cluster')
        response = routes.index(conversation)
        assert response['clusters'].first() == cluster

    def test_clusters_detail(self, conversation):
        cluster = Cluster.objects.create(clusterization=conversation.clusterization, name='cluster')
        response = routes.detail(conversation, cluster)
        assert response['cluster'] == cluster
        assert response['conversation'] == conversation

    def test_conversation_clusterize(self, conversation, user, stereotype):
        cluster = Cluster.objects.create(clusterization=conversation.clusterization, name='cluster')
        cluster.stereotypes.set([stereotype])
        response = routes.clusterize(conversation)
        assert response['content_title'] == 'Force clusterization'
        assert response['clusterization'] == conversation.clusterization


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
        response = routes.create_stereotype(request, comment.conversation)
        assert response.status_code == 302
        assert response.url == "/conversations/title/stereotypes/"

    def test_create_invalid_stereotype(self, rf, comment, user):
        data = {'name': '',
                'form-TOTAL_FORMS': 1,
                'form-INITIAL_FORMS': 0,
                'form-MIN_NUM_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                'form-0-comment': '',
                'form-0-choice': 0,
                'form-0-id': ''}
        request = rf.post('', data)
        response = routes.create_stereotype(request, comment.conversation)
        assert not response['stereotype_form'].is_valid()

    def test_edit_stereotype(self, rf, user, stereotype, comment):
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
        response = routes.edit_stereotype(request, stereotype.conversation, stereotype)
        assert response.status_code == 302
        assert response.url == "/conversations/title/stereotypes/"

    def test_edit_invalid_stereotype(self, rf, user, stereotype):
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
        response = routes.edit_stereotype(request, stereotype.conversation, stereotype)
        assert not response['votes_form'].is_valid()

    def test_edit_get_stereotype(self, rf, user, stereotype):
        request = rf.get('')
        request.user = user
        response = routes.edit_stereotype(request, stereotype.conversation, stereotype)
        assert response['stereotype_form']
        assert response['votes_form']

    def test_edit_stereotype_of_other_conversation(self, user, rf, conversation):
        another_conversation = Conversation.objects.create(title='other_conversation', author=user)
        comment = another_conversation.create_comment(user, 'comment', 'approved')
        stereotype = Stereotype.objects.create(name='stereo', conversation=conversation, owner=user)
        StereotypeVote.objects.create(author=stereotype, choice=Choice.SKIP, comment=comment)
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
        with pytest.raises(Http404):
            routes.edit_stereotype(request, another_conversation, stereotype)

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
