from django.http import Http404
from django.shortcuts import redirect

from boogie.router import Router
from .forms import ProfileForm
from ej_clusters.models import Stereotype
from ej_clusters.forms import StereotypeForm, StereotypeVoteFormSet
from ej_conversations.models import FavoriteConversation


app_name = 'ej_profiles'
urlpatterns = Router(
    template=['ej_profiles/{name}.jinja2', 'generic.jinja2'],
    login=True,
)


@urlpatterns.route('')
def detail(request):
    favorite_conversations = []
    for fav in FavoriteConversation.objects.filter(user=request.user):
        favorite_conversations.append(fav.conversation)
    return {
        'info_tab': request.GET.get('info', 'profile'),
        'profile': request.user.profile,
        'favorite_conversations': favorite_conversations,
        'favorite_count': len(favorite_conversations),
    }


@urlpatterns.route('edit/')
def edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=profile)

    return {
        'form': form,
        'profile': profile,
    }


@urlpatterns.route('comments/')
def comments(request):
    user = request.user
    return {
        'user': user,
        'comments': user.comments.all(),
        'stats': user.comments.statistics(),
    }


@urlpatterns.route('comments/<which>/')
def comments_filter(request, which):
    if which not in ('rejected', 'approved', 'pending'):
        raise Http404
    user = request.user
    return {
        'user': user,
        'comments': getattr(user.comments, which)(),
        'stats': user.comments.statistics(),
    }


#
# Profile stereotypes
#
@urlpatterns.route('stereotypes/add/', template='ej_profiles/create_stereotype.jinja2')
def create_stereotype(request):
    stereotype_form = StereotypeForm
    votes_form = StereotypeVoteFormSet
    if request.method == 'POST':
        rendered_stereotype_form = stereotype_form(request.POST)
        rendered_votes_form = votes_form(request.POST)
        if rendered_stereotype_form.is_valid() and rendered_votes_form.is_valid():
            stereotype = rendered_stereotype_form.save(commit=False)
            stereotype.owner = request.user
            stereotype.save()
            votes = rendered_votes_form.save(commit=False)
            for vote in votes:
                vote.stereotype = stereotype
                vote.save()

            return redirect('/profile/stereotypes/')
    else:
        rendered_stereotype_form = stereotype_form()
        rendered_votes_form = votes_form()
    return {
        'stereotype_form': rendered_stereotype_form,
        'votes_form': rendered_votes_form,
    }


@urlpatterns.route('stereotypes/')
def stereotypes(request):
    user_stereotypes = Stereotype.objects.filter(owner=request.user)
    return user_stereotypes
