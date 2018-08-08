from django.shortcuts import redirect

from boogie.router import Router
from .forms import ProfileForm
from ej_conversations.models import FavoriteConversation, Comment


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


@urlpatterns.route('comments/rejected/', template='ej_conversations/components/comment-list.jinja2')
def rejected_comments(request):
    user = request.user
    return {
        'user': user,
        'comments': user.comments.filter(status=Comment.STATUS.rejected),
        'stats': user.comments.statistics(),
    }


@urlpatterns.route('comments/approved/', template='ej_conversations/components/comment-list.jinja2')
def approved_comments(request):
    user = request.user
    return {
        'user': user,
        'comments': user.comments.filter(status=Comment.STATUS.approved),
        'stats': user.comments.statistics(),
    }


@urlpatterns.route('comments/pending/', template='ej_conversations/components/comment-list.jinja2')
def pending_comments(request):
    user = request.user
    return {
        'user': user,
        'comments': user.comments.filter(status=Comment.STATUS.pending),
        'stats': user.comments.statistics(),
    }
