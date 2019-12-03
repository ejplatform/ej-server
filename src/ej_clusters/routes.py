import json
from logging import getLogger

from boogie.models import F
from boogie.router import Router
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _, ugettext as __
from hyperpython import a
from hyperpython.components import fa_icon

from ej_conversations.enums import Choice
from ej_conversations.models import Conversation, Comment
from ej_conversations.routes import conversation_url, check_promoted
from . import forms
from .models import Stereotype, Cluster
from .models import StereotypeVote
from .utils import cluster_shapes

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
    clusterization = getattr(conversation, "clusterization", None)
    user_group = None

    if clusterization and clusterization.clusters.count() == 0:
        clusterization = None
    if clusterization is None:
        clusters = ()
        shapes_json = None
    else:
        try:
            clusters = (
                clusterization.clusters.annotate(size=Count(F.users))
                .annotate_attr(separated_comments=lambda c: c.separate_comments())
                .prefetch_related("stereotypes")
            )
            shapes = cluster_shapes(clusterization, clusters, user)
            shapes_json = json.dumps({"shapes": list(shapes.values())})
        except Exception as exc:
            exc_name = exc.__class__.__name__
            log.error(f"Error found during clusterization: {exc} ({exc_name})")
            clusters = ()
            shapes_json = {"shapes": [{"name": _("Error"), "size": 0, "intersections": [[0.0]]}]}
        else:
            names = list(clusterization.clusters.filter(users=user).values_list("name", flat=True))
            print(names)
            if names:
                user_group = names[0]

    can_edit = user.has_perm("ej.can_edit_conversation", conversation)
    return {
        "conversation": conversation,
        "clusters": clusters,
        "groups": {cluster.name: f"#cluster-{cluster.id}" for cluster in clusters},
        "has_edit_perm": can_edit,
        "edit_link": a(_("here"), href=conversation.url("cluster:edit")),
        "json_data": shapes_json,
        "user_group": user_group,
    }


@urlpatterns.route(conversation_url + "clusters/edit/", perms=["ej.can_edit_conversation:conversation"])
def edit(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    new_cluster_form = forms.ClusterFormNew(request=request)
    clusterization = getattr(conversation, "clusterization", None)

    # Handle POST requests for new clusters
    if request.method == "POST" and request.POST["action"] == "new" and new_cluster_form.is_valid():
        clusterization = clusterization or conversation.get_clusterization()
        new_cluster_form.save(clusterization=clusterization)
        new_cluster_form = forms.ClusterFormNew()

    # Decorate clusters
    if clusterization is None:
        clusters = ()
    else:
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


def get_stereotypes(all_stereotypes, all_votes, comments):
    stereotypes = []
    for stereotype in all_stereotypes:
        votes = [vote for vote in all_votes if vote.author == stereotype]
        voted = set(vote.comment for vote in votes)
        stereotype.non_voted_comments = [x for x in comments if x not in voted]
        stereotype.given_votes = votes
        stereotypes.append(stereotype)

    return stereotypes


def fetch_post_data(request, all_stereotypes):
    """
    Fetch data from POST dictionary
    """

    data = request.POST
    action = data["action"]
    votes = map(int, data.getlist("vote"))
    comments = map(int, data.getlist("comment"))
    stereotype = Stereotype.objects.get(id=data["stereotype"])
    if stereotype not in all_stereotypes:
        raise PermissionError

    return {
        "comments": comments,
        "votes": votes,
        "action": action,
        "stereotype": stereotype,
    }


def post_stereotype(data):
    """
    Process results and save votes
    """
    comments = Comment.objects.filter(id__in=data['comments'])
    votes = StereotypeVote.objects.filter(id__in=data['votes'])
    if data['action'] == "discard":
        votes.delete()
    else:
        choice_map = {"agree": Choice.AGREE, "disagree": Choice.DISAGREE, "skip": Choice.SKIP}
        choice = choice_map[data['action']]
        votes.update(choice=choice)
        StereotypeVote.objects.bulk_create(
            [
                StereotypeVote(choice=choice, comment=comment, author_id=data['stereotype'].id)
                for comment in comments
            ]
        )


@urlpatterns.route(conversation_url + "stereotypes/", perms=["ej.can_edit_conversation:conversation"])
def stereotype_votes(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    clusterization = conversation.get_clusterization(default=None)
    if clusterization is None:
        return {"conversation": conversation}

    # Process form, if method is post
    all_stereotypes = clusterization.stereotypes.all()
    if request.method == "POST":
        data = fetch_post_data(request, all_stereotypes)
        post_stereotype(data)

    all_votes = clusterization.stereotype_votes.all()
    comments = conversation.comments.approved()

    # Mark stereotypes with information about votes
    stereotypes = get_stereotypes(all_stereotypes, all_votes, comments)

    return {
        "conversation": conversation,
        "stereotypes": stereotypes,
        "groups": {x.name: f"#stereotype-{x.id}" for x in stereotypes},
    }


@urlpatterns.route(conversation_url + "clusters/ctrl/")
def ctrl(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user
    if not user.has_perm("ej.can_edit_conversation", conversation):
        raise PermissionError
    if request.method != "POST":
        raise PermissionError
    if request.POST["action"] == "force-clusterization":
        conversation.clusterization.update_clusterization(force=True)

    return redirect(conversation.url("cluster:index"))
