import toolz
from boogie.router import Router
from django.apps import apps
from django.db.models import Q, Count
from django.shortcuts import redirect
from django.urls import reverse

from ej_conversations.models import Conversation, Comment
from . import forms

app_name = "ej_profiles"
urlpatterns = Router(template=["ej_profiles/{name}.jinja2", "generic.jinja2"], login=True)


@urlpatterns.route("")
def detail(request):
    user = request.user
    return {
        "profile": user.get_profile(),
        "n_conversations": user.conversations.count(),
        "n_boards": user.boards.count(),
        "n_favorites": user.favorite_conversations.count(),
        "n_comments": user.comments.count(),
        "n_votes": user.votes.count(),
        "achievements_href": None,
    }


@urlpatterns.route("edit/")
def edit(request):
    profile = request.user.get_profile()
    form = forms.ProfileForm(instance=profile, request=request)

    if form.is_valid_post():
        form.files = request.FILES
        form.save()
        from pprint import pprint

        pprint(form.cleaned_data)
        return redirect("/profile/")

    return {"form": form, "profile": profile}


@urlpatterns.route("contributions/")
def contributions(request):
    user = request.user

    # Fetch all conversations the user created
    created = user.conversations.cache_annotations("first_tag", "n_user_votes", "n_comments", user=user)

    # Fetch voted conversations
    # This code merges in python 2 querysets. The first is annotated with
    # tag and the number of user votes. The second is annotated with the total
    # number of comments in each conversation
    voted = user.conversations_with_votes.exclude(id__in=[x.id for x in created])
    voted = voted.cache_annotations("first_tag", "n_user_votes", user=user)
    voted_extra = (
        Conversation.objects.filter(id__in=[x.id for x in voted])
        .cache_annotations("n_comments")
        .values("id", "n_comments")
    )
    total_votes = {}
    for item in voted_extra:
        total_votes[item["id"]] = item["n_comments"]
    for conversation in voted:
        conversation.annotation_total_votes = total_votes[conversation.id]

    # Now we get the favorite conversations from user
    favorites = Conversation.objects.filter(favorites__user=user).cache_annotations(
        "first_tag", "n_user_votes", "n_comments", user=user
    )

    # Comments
    comments = user.comments.select_related("conversation").annotate(
        skip_count=Count("votes", filter=Q(votes__choice=0)),
        agree_count=Count("votes", filter=Q(votes__choice__gt=0)),
        disagree_count=Count("votes", filter=Q(votes__choice__lt=0)),
    )
    groups = toolz.groupby(lambda x: x.status, comments)
    approved = groups.get(Comment.STATUS.approved, ())
    rejected = groups.get(Comment.STATUS.rejected, ())
    pending = groups.get(Comment.STATUS.pending, ())

    return {
        "profile": user.profile,
        "user": user,
        "created_conversations": created,
        "favorite_conversations": favorites,
        "voted_conversations": voted,
        "approved_comments": approved,
        "rejected_comments": rejected,
        "pending_comments": pending,
    }
