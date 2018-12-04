from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a, input_, label, Block
from hyperpython.components import html_list, html_table

from boogie.router import Router
from boogie.rules import proxy_seq
from ej_clusters.forms import StereotypeForm, StereotypeVoteCreateFormSet, StereotypeVoteEditFormSet
from ej_conversations import Choice
from ej_conversations.models import Conversation, Comment
from .models import Stereotype, Cluster, StereotypeVote, Clusterization

app_name = 'ej_cluster'
urlpatterns = Router(
    template=['ej_clusters/{name}.jinja2', 'generic.jinja2'],
    login=True,
    models={
        'conversation': Conversation,
        'stereotype': Stereotype,
        'cluster': Cluster,
    },
    lookup_field={'conversation': 'slug'},
    lookup_type={'conversation': 'slug'},
)


#
# Cluster info
#
@urlpatterns.route('conversations/<model:conversation>/clusters/', template='ej_clusters/list-cluster.jinja2',
                   perms=['ej.can_edit_conversation:conversation'])
def index(conversation):
    clusters = proxy_seq(
        conversation.clusters.all(),
        info=cluster_info,
    )
    return {
        'content_title': _('Clusters'),
        'conversation': conversation,
        'clusters': clusters,
    }


@urlpatterns.route('conversations/<model:conversation>/clusters/<model:cluster>/',
                   perms=['ej.can_edit_conversation:conversation'])
def detail(conversation, cluster):
    return {
        'conversation': conversation,
        'cluster': cluster,
    }


@urlpatterns.route('conversations/<model:conversation>/clusterize/',
                   perms=['ej.can_edit_conversation:conversation'])
def clusterize(conversation):
    clusterization = conversation.get_clusterization(None)
    if clusterization is not None:
        clusterization.update_clusterization(force=True)
    return {
        'content_title': _('Force clusterization'),
        'clusterization': clusterization,
        'conversation': conversation,
    }


#
# Stereotypes
#
@urlpatterns.route('conversations/<model:conversation>/stereotypes/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def stereotype_list(conversation):
    clusterization = conversation.get_clusterization(None)
    stereotypes = () if clusterization is None else clusterization.stereotypes.all()
    return {
        'content_title': _('Stereotypes'),
        'conversation_title': conversation.title,
        'stereotypes': stereotypes,
        'stereotype_url': conversation.get_absolute_url() + 'stereotypes/',
        'conversation_url': conversation.get_absolute_url(),
    }


@urlpatterns.route('conversations/<model:conversation>/stereotypes/add/',
                   perms=['ej.can_manage_stereotypes:conversation'])
def create_stereotype(request, conversation):
    return create_stereotype_context(request, conversation)


@urlpatterns.route('conversations/<model:conversation>/stereotypes/<model:stereotype>/edit/',
                   perms=['ej.can_manage_stereotypes:stereotype'])
def edit_stereotype(request, conversation, stereotype):
    return edit_stereotype_context(request, conversation, stereotype)


@urlpatterns.route('conversations/<model:conversation>/stereotypes/<model:stereotype>/',
                   perms=['ej.can_manage_stereotypes:stereotype'])
def stereotype_vote(request, conversation, stereotype):
    if request.method == 'POST':
        for k, v in request.POST.items():
            if k.startswith('choice-'):
                pk = int(k[7:])
                comment = Comment.objects.get(pk=pk, conversation=conversation)
                stereotype.vote(comment, v.lower())

    title = _('Stereotype votes ({conversation})').format(conversation=conversation)
    non_voted_comments = stereotype.non_voted_comments(conversation)
    voted_comments = stereotype.voted_comments(conversation)

    return {
        'content_title': title,
        'conversation': conversation,
        'stereotype': stereotype,
        'non_voted_table': votes_table(non_voted_comments),
        'voted_table': votes_table(voted_comments),
        'non_voted_comments_count': non_voted_comments.count(),
        'voted_comments_count': non_voted_comments.count(),
    }


#
# User profile
#
@urlpatterns.route('profile/clusters/')
def list_cluster(request):
    user_clusters = Cluster.objects.filter(clusterization__conversation__author=request.user)
    return {
        'clusters': user_clusters,
        'create_url': '/profile/clusters/add/',
    }


#
# Auxiliary functions
#
def create_stereotype_context(request, conversation):
    if request.method == 'POST':
        stereotype_form = StereotypeForm(request.POST, owner=request.user)
        votes_formset = StereotypeVoteCreateFormSet(request.POST)

        if stereotype_form.is_valid() and votes_formset.is_valid():
            stereotype = stereotype_form.save()
            for vote in votes_formset.save(commit=False):
                vote.author = stereotype
                vote.save()
            clusterization = Clusterization.objects.get(conversation=conversation)
            cluster = Cluster(clusterization=clusterization, name=stereotype.name)
            cluster.save()
            cluster.stereotypes.add(stereotype)
            return redirect(conversation.get_absolute_url() + 'stereotypes/')

    else:
        stereotype_form = StereotypeForm(owner=request.user)
        votes_formset = StereotypeVoteCreateFormSet(queryset=StereotypeVote.objects.none())

    comments = Comment.objects.filter(conversation=conversation)
    for form in votes_formset:
        form.fields['comment'].queryset = comments
    return {
        'stereotype_form': stereotype_form,
        'votes_form': votes_formset,
        'conversation_title': conversation.title,
    }


def edit_stereotype_context(request, conversation, stereotype):
    if stereotype.owner != request.user:
        raise Http404
    if request.method == 'POST':
        stereotype_form = StereotypeForm(request.POST, instance=stereotype)
        votes = StereotypeVote.objects.filter(author=stereotype)
        votes_formset = StereotypeVoteEditFormSet(request.POST, queryset=votes)

        if stereotype_form.is_valid() and votes_formset.is_valid():
            stereotype = stereotype_form.save()
            for vote in votes_formset.save(commit=False):
                vote.author = stereotype
                vote.save()
            return redirect(conversation.get_absolute_url() + 'stereotypes/')
    else:
        stereotype_form = StereotypeForm(instance=stereotype)
        votes = StereotypeVote.objects.filter(author=stereotype)
        votes_formset = StereotypeVoteEditFormSet(queryset=votes)

        comments = Comment.objects.filter(conversation=conversation)
        for form in votes_formset:
            form.fields['comment'].queryset = comments

    return {
        'stereotype_form': stereotype_form,
        'votes_form': votes_formset,
        'conversation_title': conversation.title,
    }


def cluster_info(cluster):
    stereotypes = cluster.stereotypes.all()
    user_data = [
        (user.username, user.name)
        for user in cluster.users.all()
    ]
    return {
        'size': cluster.users.count(),
        'stereotypes': stereotypes,
        'stereotype_links': [
            a(str(stereotype),
              href=reverse(
                  'cluster:stereotype-vote', kwargs={
                      'conversation': cluster.conversation,
                      'stereotype': stereotype,
                  }))
            for stereotype in stereotypes
        ],
        'users': html_table(user_data, columns=[_('Username'), _('Name')])
    }


def votes_table(comments):
    if comments:
        data = [
            [i, comment, vote_options(comment)]
            for i, comment in enumerate(comments, 1)
        ]
        return html_table(data, columns=['', _('Comment'), _('Options')], class_='table')
    else:
        return None


def vote_options(comment):
    def vote_option(choice):
        kwargs = {'checked': True} if choice == voted else {}
        return Block([
            label([
                input_(value=choice.name, name=name, type='radio', **kwargs),
                choice.description,
            ]),
        ])

    voted = getattr(comment, 'choice', None)
    name = f'choice-{comment.id}'
    choices = [Choice.AGREE, Choice.SKIP, Choice.DISAGREE]
    return html_list(map(vote_option, choices), class_='unlist')
