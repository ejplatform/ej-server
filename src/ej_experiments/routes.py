from logging import getLogger

from boogie.router import Router
from django.contrib.auth import get_user_model

from ej_conversations.models import Conversation, Vote
from . import forms

urlpatterns = Router(template="ej_experiments/{name}.jinja2", login=True)
app_name = "ej_experiments"
log = getLogger("ej")
User = get_user_model()


@urlpatterns.route("")
def index(request):
    user_form = forms.CreateUsersForm()
    conversations_form = forms.CreateConversationsForm()
    votes_form = forms.CreateVotesForm()

    if request.method == "POST":
        action = request.POST["action"]

        if action == "create-users":
            user_form = forms.CreateUsersForm(request=request)
            if user_form.is_valid():
                user_form.create()
        elif action == "create-conversations":
            conversations_form = forms.CreateConversationsForm(request=request)
            if conversations_form.is_valid():
                conversations_form.create()
        elif action == "create-votes":
            votes_form = forms.CreateVotesForm(request=request)
            if votes_form.is_valid():
                votes_form.create()

    return {
        "n_users": User.objects.count(),
        "n_conversations": Conversation.objects.count(),
        "n_votes": Vote.objects.count(),
        "users_form": user_form,
        "conversations_form": conversations_form,
        "votes_form": votes_form,
    }
