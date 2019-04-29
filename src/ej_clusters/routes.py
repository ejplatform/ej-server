from logging import getLogger

from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _, ugettext as __
from hyperpython import a
from hyperpython.components import fa_icon

from boogie.models import F
from boogie.router import Router
from ej_conversations.enums import Choice
from ej_conversations.models import Conversation, Comment
from ej_conversations.routes import conversation_url, check_promoted
from . import forms
from .models import Stereotype, Cluster
from .models import StereotypeVote

log = getLogger("ej")
app_name = "ej_cluster"
urlpatterns = Router(
    template="ej_clusters/{name}.jinja2",
    login=True,
    models={"conversation": Conversation, "stereotype": Stereotype, "cluster": Cluster},
)
stereotype_perms = {"perms": ["ej.can_manage_stereotypes:conversation"]}


#
# Cluster visualization
#
@urlpatterns.route(conversation_url + "clusters/")
def index(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user
    participants = conversation.users.count()
    clusters = (
        conversation.clusters.annotate(size=Count(F.users))
        .annotate_attr(
            size_pc=lambda obj: int(100 * obj.size / participants),
            cohesion_category=_("high"),
            cohesion_pc=80,
            typical_comments=[],
        )
        .prefetch_related("stereotypes")
    )

    return {
        "conversation": conversation,
        "clusters": clusters,
        "groups": {cluster.name: f"#cluster-{cluster.id}" for cluster in clusters},
        "participants": participants,
        "is_conversation_admin": user.has_perm(
            "ej.can_edit_conversation", conversation
        ),
        "edit_link": a(_("here"), href=conversation.url("cluster:edit")),
    }


@urlpatterns.route(conversation_url + "clusters/edit/")
def edit(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    new_cluster_form = forms.ClusterFormNew(request=request)
    clusterization = conversation.get_clusterization()

    # Handle POST requests for new clusters
    if (
        request.method == "POST"
        and request.POST["action"] == "new"
        and new_cluster_form.is_valid()
    ):
        new_cluster_form.save(clusterization=clusterization)
        new_cluster_form = forms.ClusterFormNew()

    # Decorate clusters
    clusters = clusterization.clusters.annotate_attr(
        form=lambda x: forms.ClusterForm(request=request, instance=x)
    )
    groups = [
        (fa_icon("plus", alt=__("Create new group")), "#cluster-new"),
        # (_('New'), '#cluster-new'),
        *((cluster.name, f"#cluster-{cluster.id}") for cluster in clusters),
    ]

    # Handle POST requests for existing clusters
    if request.method == "POST" and request.POST["action"] != "new":
        cluster_map = {x.id: x for x in clusters}
        cluster = cluster_map[int(request.POST["action"])]
        if request.POST["submit"] == "delete":
            cluster.delete()
            return redirect(conversation.url("cluster:edit"))
        elif cluster.form.is_valid():
            cluster.form.save()
            cluster.form = forms.ClusterForm(instance=cluster)

    return {
        "conversation": conversation,
        "groups": groups,
        "clusters": clusters,
        "new_cluster_form": new_cluster_form,
    }


@urlpatterns.route(
    conversation_url + "stereotypes/", perms=["ej.can_edit_conversation:conversation"]
)
def stereotype_votes(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    clusterization = conversation.get_clusterization(default=None)
    if clusterization is None:
        return {"conversation": conversation}

    # Process form, if method is post
    all_stereotypes = clusterization.stereotypes.all()
    if request.method == "POST":
        # Fetch data from POST dictionary
        data = request.POST
        action = data["action"]
        votes = map(int, data.getlist("vote"))
        comments = map(int, data.getlist("comment"))
        stereotype = Stereotype.objects.get(id=data["stereotype"])
        if stereotype not in all_stereotypes:
            raise PermissionError

        # Process results and save votes
        comments = Comment.objects.filter(id__in=comments)
        votes = StereotypeVote.objects.filter(id__in=votes)
        if action == "discard":
            votes.delete()
        else:
            choice_map = {
                "agree": Choice.AGREE,
                "disagree": Choice.DISAGREE,
                "skip": Choice.SKIP,
            }
            choice = choice_map[action]
            votes.update(choice=choice)
            StereotypeVote.objects.bulk_create(
                [
                    StereotypeVote(
                        choice=choice, comment=comment, author_id=stereotype.id
                    )
                    for comment in comments
                ]
            )

    all_votes = clusterization.stereotype_votes.all()
    comments = conversation.comments.all()

    # Mark stereotypes with information about votes
    stereotypes = []
    for stereotype in all_stereotypes:
        votes = [vote for vote in all_votes if vote.author == stereotype]
        voted = set(vote.comment for vote in votes)
        stereotype.non_voted_comments = [x for x in comments if x not in voted]
        stereotype.given_votes = votes
        stereotypes.append(stereotype)

    return {
        "conversation": conversation,
        "stereotypes": stereotypes,
        "groups": {x.name: f"#stereotype-{x.id}" for x in stereotypes},
    }
