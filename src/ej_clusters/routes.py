import json
from logging import getLogger

from rest_framework.response import Response
from boogie.models import F
from boogie.router import Router
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _, gettext as __
from hyperpython import a
from hyperpython.components import fa_icon
from django.http import HttpResponse
from ej_conversations.enums import Choice
from ej_conversations.models import Conversation, Comment

from . import forms
from .models import Stereotype, Cluster
from .models import StereotypeVote
from .utils import cluster_shapes

from ej_conversations.utils import check_promoted
from ej_clusters.stereotypes_utils import extract_choice_id, stereotype_vote_information

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
    created_vote_id = None
    if clusterization is None:
        return {"conversation": conversation}

    all_stereotypes = clusterization.stereotypes.all()
    stereotype = all_stereotypes.first()
    order_votes_by = 1

    if request.method == "GET":
        if "stereotype-select" in request.GET:
            stereotype = Stereotype.objects.get(id=request.GET["stereotype-select"])

    if request.method == "POST":
        # Fetch data from POST dictionary
        data = request.POST
        stereotype = Stereotype.objects.get(id=data["stereotype"])
        if stereotype not in all_stereotypes:
            raise PermissionError

        choice_map = {"agree": Choice.AGREE, "disagree": Choice.DISAGREE, "skip": Choice.SKIP}

        if "update" in data:
            action_object_id = extract_choice_id(data["update"])
            if action_object_id["choice"] == "delete":
                StereotypeVote.objects.get(pk=action_object_id["id"]).delete()
            else:
                choice = choice_map[action_object_id["choice"]]
                StereotypeVote.objects.filter(pk=action_object_id["id"]).update(choice=choice)
    return {
        "conversation": conversation,
        "stereotype": stereotype_vote_information(stereotype, clusterization, conversation, order_votes_by),
        "groups": {x.name: f"{x.id}" for x in clusterization.stereotypes.all()} or None,
        "order_votes_by": order_votes_by,
        "created_vote_id": created_vote_id,
    }


@urlpatterns.route(
    conversation_url + "stereotypes/stereotype-votes-ordenation",
    perms=["ej.can_edit_conversation:conversation"],
)
def stereotype_votes_ordenation(request, conversation, **kwargs):
    sort_order = request.GET.get("sort")
    order_votes_by_choice = request.GET.get("orderBy")
    clusterization = conversation.get_clusterization(default=None)
    stereotype = Stereotype.objects.get(id=request.GET.get("stereotypeId"))
    return render(
        request,
        "ej_clusters/stereotype-votes/stereotype-given-votes.jinja2",
        {
            "stereotype": stereotype_vote_information(
                stereotype, clusterization, conversation, order_votes_by_choice, sort_order
            ),
        },
    )


@urlpatterns.route(
    conversation_url + "stereotypes/stereotype-votes/create",
    perms=["ej.can_edit_conversation:conversation"],
)
def stereotype_votes_create(request, conversation, **kwargs):
    if request.method == "POST":
        comment = request.POST.get("comment")
        stereotype_id = request.POST.get("author")
        choice = request.POST.get("choice")
        stereotype_vote = StereotypeVote.objects.create(
            choice=int(choice), comment_id=comment, author_id=stereotype_id
        )
    return HttpResponse(stereotype_vote.id)


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
