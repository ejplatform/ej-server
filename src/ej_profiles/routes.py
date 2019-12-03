import toolz
from boogie.router import Router
from django.apps import apps
from django.db.models import Q, Count
from django.shortcuts import redirect
from django.urls import reverse

from ej_conversations.models import Conversation, Comment
from . import forms
from .utils import get_loc, get_client_ip

app_name = "ej_profiles"
urlpatterns = Router(template=["ej_profiles/{name}.jinja2", "generic.jinja2"], login=True)


@urlpatterns.route("")
def detail(request):
    user = request.user
    return {
        "profile": user.get_profile(),
        "n_conversations": user.conversations.count(),
        "n_favorites": user.favorite_conversations.count(),
        "n_comments": user.comments.count(),
        "n_votes": user.votes.count(),
        "achievements_href": reverse("gamification:achievements")
        if apps.is_installed("ej_gamification")
        else None,
    }


@urlpatterns.route("edit/")
def edit(request):
    profile = request.user.get_profile()
    form = forms.ProfileForm(instance=profile, request=request)

    ip_adr = get_client_ip(request)

    location = get_loc(ip_adr)

    if form.is_valid_post():
        form.files = request.FILES

        if location.country is not None:
            profile = check_location(profile, location)

        form.save()

        from pprint import pprint
        pprint(form.cleaned_data)
        return redirect("/profile/")

    return {"form": form, "profile": profile}


def check_location(profile, location):
    if not profile.country:
        profile.country = location.country
    if not profile.state:
        profile.state = location.state
    if not profile.city:
        profile.city = location.city

    return profile


def get_voted(user):
    """
    Fetch voted conversations
    This code merges in python 2 querysets. The first is annotated with
    tag and the number of user votes. The second is annotated with the total
    number of comments in each conversation
    """
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

    return voted


def get_groups(user):
    comments = user.comments.select_related("conversation").annotate(
        skip_count=Count("votes", filter=Q(votes__choice=0)),
        agree_count=Count("votes", filter=Q(votes__choice__gt=0)),
        disagree_count=Count("votes", filter=Q(votes__choice__lt=0)),
    )
    return toolz.groupby(lambda x: x.status, comments)


@urlpatterns.route("contributions/")
def contributions(request):
    
    user = request.user

    """
    Fetch all conversations the user created
    """
    created = user.conversations.cache_annotations("first_tag", "n_user_votes", "n_comments", user=user)

    voted = get_voted(user)

    """
    Now we get the favorite conversations from user
    """
    favorites = Conversation.objects.filter(favorites__user=user).cache_annotations(
        "first_tag", "n_user_votes", "n_comments", user=user
    )
    """
    Comments
    """
    groups = get_groups(user)
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
