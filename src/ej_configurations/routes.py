from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from django.utils.translation import ugettext as _

from boogie.router import Router
from ej_conversations.models import Conversation, Comment, Vote

urlpatterns = Router()


@urlpatterns.route('', staff=True)
def index(request):
    return render(request, 'configurations/index.jinja2', {})


@urlpatterns.route('info/', staff=True)
def info(request):
    ctx = dict(
        # Generic info
        user_count=count(get_user_model()),
        flatpages=FlatPage.objects.values_list('url'),

        # Conversations
        conversations_counts={
            _('Conversations'): count(Conversation),
            _('Votes'): count(Vote),
            _('Comments'): count(Comment),
        }
    )
    return render(request, 'configurations/info.jinja2', ctx)


@urlpatterns.route('fragment/', staff=True)
def fragment_list(request):
    ctx = {}
    return render(request, 'configurations/fragment-list.jinja2', ctx)


@urlpatterns.route('fragment/<name>/')
def fragment_error(request, name):
    ctx = {
        'name': name,
    }
    return render(request, 'configurations/fragment-error.jinja2', ctx)


@urlpatterns.route('styles/')
def styles(request):
    ctx = {}
    return render(request, 'configurations/styles.jinja2', ctx)


#
# Utility functions
#
def count(model):
    return model.objects.count()
