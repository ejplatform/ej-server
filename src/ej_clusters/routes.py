from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from hyperpython import input_, label, Block
from hyperpython.components import html_list, html_table

from boogie.models import F
from boogie.router import Router
from ej_conversations.enums import Choice
from ej_conversations.models import Conversation, Comment
from ej_conversations.routes import conversation_url, check_promoted
from .models import Stereotype, Cluster

app_name = 'ej_cluster'
urlpatterns = Router(
    template=['ej_clusters/{name}.jinja2', 'generic.jinja2'],
    login=True,
    models={
        'conversation': Conversation,
        'stereotype': Stereotype,
        'cluster': Cluster,
    },
)
stereotype_perms = {'perms': ['ej.can_manage_stereotypes:conversation']}


#
# Cluster visualization
#
@urlpatterns.route(conversation_url + 'clusters/')
def index(conversation, slug, check=check_promoted):
    return {
        'conversation': conversation,
        'clusters': conversation.clusters
            .annotate(size=Count(F.users))
            .prefetch_related('stereotypes'),
    }


@urlpatterns.route(conversation_url + 'stereotypes/<model:stereotype>/',
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
# Auxiliary functions
#
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
