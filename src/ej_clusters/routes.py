import json
from logging import getLogger

from rest_framework.response import Response
from boogie.models import F
from boogie.router import Router
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _, ugettext as __
from hyperpython import a
from hyperpython.components import fa_icon

from ej_conversations.enums import Choice
from ej_conversations.models import Conversation, Comment

from . import forms
from .models import Stereotype, Cluster
from .models import StereotypeVote
from .utils import cluster_shapes

from ej_conversations.utils import check_promoted

log = getLogger("ej")
app_name = "ej_cluster"
urlpatterns = Router(
    template="ej_clusters/{name}.jinja2",
    login=True,
    models={"conversation": Conversation, "stereotype": Stereotype, "cluster": Cluster},
)
stereotype_perms = {"perms": ["ej.can_manage_stereotypes:conversation"]}

conversation_url = f"<model:conversation>/<slug:slug>/"

#
# Cluster visualization
#
@urlpatterns.route(conversation_url + "clusters/")
def index(request, conversation, **kwargs):
    check_promoted(conversation, request)
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
def edit(request, conversation, **kwargs):
    check_promoted(conversation, request)

    # Decorate clusters
    clusters = get_conversation_clusters_decorated_with_forms(conversation, request)

    if request.method == "GET":
        return get_edit_view(request, clusters, conversation)
    elif request.method == "POST":
        return post_edit_view(request, conversation, clusters)
    return Response(status=403)


@urlpatterns.route(conversation_url + "stereotypes/", perms=["ej.can_edit_conversation:conversation"])
def stereotype_votes(request, conversation, **kwargs):
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
            choice_map = {"agree": Choice.AGREE, "disagree": Choice.DISAGREE, "skip": Choice.SKIP}
            choice = choice_map[action]
            votes.update(choice=choice)
            StereotypeVote.objects.bulk_create(
                [
                    StereotypeVote(choice=choice, comment=comment, author_id=stereotype.id)
                    for comment in comments
                ]
            )

    all_votes = clusterization.stereotype_votes.all()
    comments = conversation.comments.approved()

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


@urlpatterns.route(conversation_url + "clusters/ctrl/")
def ctrl(request, board, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user
    if not user.has_perm("ej.can_edit_conversation", conversation):
        raise PermissionError
    if request.method != "POST":
        raise PermissionError
    if request.POST["action"] == "force-clusterization":
        conversation.clusterization.update_clusterization(force=True)

    return redirect(conversation.url("cluster:index"))


def get_edit_view(request, clusters, conversation):
    new_cluster_form = forms.ClusterFormNew(user=conversation.author)
    edit_cluster = None
    show_modal = False
    DELETED_GROUP = "deleted_group"

    if "cluster-select" in request.GET:
        current_cluster_select = request.GET["cluster-select"]
        if current_cluster_select != "new":
            new_cluster_form = None
            edit_cluster = clusters.get(id=current_cluster_select)
    elif "delete-success" in request.GET:
        show_modal = DELETED_GROUP

    return {
        "conversation": conversation,
        "clusters": clusters,
        "new_cluster_form": new_cluster_form,
        "edit_cluster": edit_cluster,
        "show_modal": show_modal,
    }


def post_edit_view(request, conversation, clusters):
    new_cluster_form = forms.ClusterFormNew(request=request, user=conversation.author)
    edit_cluster = None
    show_modal = False
    CREATED_GROUP = "created_group_modal"

    # Handle POST requests for new clusters
    if request.POST["action"] == "new" and new_cluster_form.is_valid():
        clusterization = conversation.get_clusterization()
        new_cluster_form.save(clusterization=clusterization)
        new_cluster_form = forms.ClusterFormNew(user=conversation.author)
        show_modal = CREATED_GROUP
        clusters = get_conversation_clusters_decorated_with_forms(conversation, request)

    # Handle POST requests for existing clusters
    if request.POST["action"] != "new":
        new_cluster_form = None
        cluster_map = {x.id: x for x in clusters}
        cluster = cluster_map[int(request.POST["action"])]
        if "delete" in request.POST:
            cluster.delete()
            return redirect(conversation.url("cluster:edit") + "?delete-success")
        elif cluster.form.is_valid():
            edit_cluster = cluster.form.save()
            edit_cluster.form = forms.ClusterForm(instance=edit_cluster, user=conversation.author)

    return {
        "conversation": conversation,
        "clusters": clusters,
        "new_cluster_form": new_cluster_form,
        "edit_cluster": edit_cluster,
        "show_modal": show_modal,
    }


def get_conversation_clusters_decorated_with_forms(conversation, request):
    clusterization = getattr(conversation, "clusterization", None)
    if clusterization is None:
        clusters = ()
    else:
        clusters = clusterization.clusters.annotate_attr(
            form=lambda x: forms.ClusterForm(request=request, instance=x, user=conversation.author)
        )
    return clusters
