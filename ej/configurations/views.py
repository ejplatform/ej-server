import functools
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden

from ej_conversations.models import Category, Conversation, Comment, Vote, Stereotype, StereotypeVote

User = get_user_model()


def staff_required(view):
    @functools.wraps(view)
    def decorated(request, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        return view(request, **kwargs)

    return decorated


@staff_required
def index(request):
    return render(request, 'configurations/index.jinja2', {})


@staff_required
def info(request):
    """
    Generic site info.
    """
    ctx = dict(
        # Generic info
        user_count=count(User),
        flatpages=FlatPage.objects.values_list('url'),

        # Conversations
        conversations_counts={
            _('Categories'): count(Category),
            _('Conversations'): count(Conversation),
            _('Votes'): count(Vote),
            _('Comments'): count(Comment),
            _('Stereotypes'): count(Stereotype),
            _('Stereotypes votes'): count(StereotypeVote),
        }
    )
    return render(request, 'configurations/info.jinja2', ctx)


def fragment_error(request, name):
    ctx = {
        'name': name,
    }
    return render(request, 'configurations/fragment-error.jinja2', ctx)


@staff_required
def fragment_list(request):
    ctx = {}
    return render(request, 'configurations/fragment-list.jinja2', ctx)


def styles(request):
    ctx = {}
    return render(request, 'configurations/styles.jinja2', ctx)


#
# Utility functions
#
def count(model):
    return model.objects.count()
