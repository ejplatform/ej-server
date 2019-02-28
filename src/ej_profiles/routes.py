from boogie.router import Router
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ej_conversations.models import Conversation, FavoriteConversation, Comment
from .forms import ProfileForm, UsernameForm

app_name = 'ej_profiles'
urlpatterns = Router(
    template=['ej_profiles/{name}.jinja2', 'generic.jinja2'],
    login=True,
)


@urlpatterns.route('')
def detail(request):
    user = request.user
    return {
        'profile': user.profile,
        'n_conversations': user.conversations.count(),
        'n_favorites': user.favorite_conversations.count(),
        'n_comments': user.comments.count(),
        'n_votes': user.votes.count(),
    }


@urlpatterns.route('edit/')
def edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, files=request.FILES)
        name_form = UsernameForm(request.POST, instance=request.user)
        if form.is_valid() and name_form.is_valid():
            form.save()
            name_form.save()
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=profile)
        name_form = UsernameForm(instance=request.user)

    return {
        'form': form,
        'name_form': name_form,
        'profile': profile,
    }


@urlpatterns.route('contributions/')
def contributions(request):
    user = request.user
    return {
        'profile': user.profile,
        'user': user,
        'created_conversations': user.conversations.all(),
        'favorite_conversations': user.favorite_conversations.all(),
        'approved_comments': user.comments.approved(),
        'rejected_comments': user.comments.rejected(),
        'pending_comments': user.comments.pending(),
        'voted_conversations': Conversation.objects.filter(comments__votes__author=user).distinct(),
    }
