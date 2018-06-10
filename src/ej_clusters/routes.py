from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_conversations.models import Conversation, Choice, Comment
from hyperpython import a, input_, label, Block, p
from hyperpython.components import html_list, html_table
from .models import Stereotype, Cluster

app_name = 'ej_cluster'
urlpatterns = Router(
    template=['ej_clusters/{name}.jinja2', 'generic.jinja2'],
    perms=['ej_converations.can_edit_conversation'],
    object='conversation',
    login=True,
    models={
        'conversation': Conversation,
        'stereotype': Stereotype,
    },
    lookup_field={'conversation': 'slug'},
    lookup_type={'conversation': 'slug'},
)
conversation_url = '<model:conversation>/'


#
# Cluster info
#
@urlpatterns.route(conversation_url + 'clusters/')
def index(conversation):
    return {
        'conversation': conversation,
    }


@urlpatterns.route(conversation_url + 'clusters/<int:index>/')
def detail(conversation, index):
    cluster = get_object_or_404(Cluster, conversation=conversation, index=index)
    return {
        'conversation': conversation,
        'cluster': cluster,
    }


#
# Stereotypes
#
@urlpatterns.route(conversation_url + 'stereotypes/')
def stereotype_list(conversation):
    base_href = f'{conversation.get_absolute_url()}stereotypes/'
    return {
        'content_title': _('Stereotypes'),
        'conversation': conversation,
        'stereotypes': html_list(
            a(str(stereotype), href=f'{base_href}{stereotype.id}/')
            for stereotype in conversation.stereotypes.all()
        ),
    }


@urlpatterns.route(conversation_url + 'stereotypes/<model:stereotype>/')
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
        'non_voted_table': votes_table(non_voted_comments[:5]),
        'voted_table': votes_table(voted_comments[:5]),
        'non_voted_comments_count': non_voted_comments.count(),
        'voted_comments_count': non_voted_comments.count(),
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
