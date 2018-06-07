from django.http import Http404
from django.shortcuts import redirect

from boogie.router import Router
from .forms import ProfileForm

from ej.utils.perms import conversations
from ej_conversations.models.conversation import Conversation
from ej_conversations.rules import can_moderate_conversation


urlpatterns = Router(
    template='ej_profiles/{name}.jinja2',
    login=True,
)


@urlpatterns.route('')
def detail(request):
    return {
        'info_tab': request.GET.get('info', 'profile'),
        'conversations': conversations(
            request.user,
            [can_moderate_conversation],
            Conversation.objects.filter(author=request.user)
        )
    }


@urlpatterns.route('edit/')
def edit(request):
    profile = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=request.user)

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
        'stats': user.comments.stats(),
    }


@urlpatterns.route('comments/<which>/')
def comments_filter(request, which):
    if which not in ('rejected', 'approved', 'pending'):
        raise Http404
    user = request.user
    return {
        'user': user,
        'comments': getattr(user.comments, which)(),
        'stats': user.comments.stats(),
    }
