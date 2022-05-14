import json
from logging import getLogger

from boogie.models import F
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as __, gettext_lazy as _
from ej.decorators import can_edit_conversation
from ej_clusters.stereotypes_utils import extract_choice_id, stereotype_vote_information
from ej_conversations.enums import Choice
from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
from hyperpython import a
from rest_framework.response import Response

from . import forms
from .models import Stereotype
from .models import StereotypeVote
from .utils import cluster_shapes

log = getLogger("ej")

#
# Cluster visualization
#
def index(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    check_promoted(conversation, request)
    user = request.user
    clusterization = getattr(conversation, "clusterization", None)

    if clusterization and clusterization.clusters.count() == 0:
        clusterization = None

    json_shape_user_group = get_json_shape_user_group_from_clusterization(clusterization, user)

    can_edit = user.has_perm("ej.can_edit_conversation", conversation)
    render_context = {
        "conversation": conversation,
        "groups": {cluster.name: f"#cluster-{cluster.id}" for cluster in json_shape_user_group["clusters"]},
        "has_edit_perm": can_edit,
        "edit_link": a(
            _("here"),
            href=reverse(
                "boards:cluster-edit",
                kwargs={
                    "conversation_id": conversation.id,
                    "slug": conversation.slug,
                    "board_slug": conversation.board.slug,
                },
            ),
        ),
    }
    return render(request, "ej_clusters/index.jinja2", dict(render_context, **json_shape_user_group))


@login_required
@can_edit_conversation
def edit(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    check_promoted(conversation, request)

    # Decorate clusters
    clusters = get_conversation_clusters_decorated_with_forms(conversation, request)

    if request.method == "GET":
        render_context = get_edit_view(request, clusters, conversation)
        return render(request, "ej_clusters/edit.jinja2", render_context)
    elif request.method == "POST":
        render_context = post_edit_view(request, conversation, clusters)
        return render(request, "ej_clusters/edit.jinja2", render_context)
    return Response(status=403)


@login_required
@can_edit_conversation
def stereotype_votes(request, conversation_id, **kwargs):
    conversation = Conversation.objects.get(id=conversation_id)
    clusterization = conversation.get_clusterization(default=None)
    created_vote_id = None
    if clusterization is None:
        render_context = {"conversation": conversation, "groups": None}
        return render(request, "ej_clusters/stereotype-votes.jinja2", render_context)

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
    render_context = {
        "conversation": conversation,
        "stereotype": stereotype_vote_information(stereotype, clusterization, conversation, order_votes_by),
        "groups": {x.name: f"{x.id}" for x in clusterization.stereotypes.all()} or None,
        "order_votes_by": order_votes_by,
        "created_vote_id": created_vote_id,
    }
    return render(request, "ej_clusters/stereotype-votes.jinja2", render_context)


@login_required
@can_edit_conversation
def stereotype_votes_ordenation(request, conversation_id, **kwargs):
    stereotype_id = request.GET.get("stereotypeId")
    conversation = Conversation.objects.get(id=conversation_id)

    if stereotype_id:
        sort_order = request.GET.get("sort")
        order_votes_by_choice = request.GET.get("orderBy")
        clusterization = conversation.get_clusterization(default=None)
        stereotype = Stereotype.objects.get(id=stereotype_id)
        return render(
            request,
            "ej_clusters/stereotype-votes/stereotype-given-votes.jinja2",
            {
                "stereotype": stereotype_vote_information(
                    stereotype, clusterization, conversation, order_votes_by_choice, sort_order
                ),
            },
        )

    kwargs = conversation.get_url_kwargs()
    return redirect(reverse("boards:cluster-stereotype_votes", kwargs=kwargs))


@login_required
@can_edit_conversation
def stereotype_votes_create(request, conversation_id, **kwargs):
    if request.method == "POST":
        comment = request.POST.get("comment")
        stereotype_id = request.POST.get("author")
        choice = request.POST.get("choice")
        stereotype_vote = StereotypeVote.objects.create(
            choice=int(choice), comment_id=comment, author_id=stereotype_id
        )
        return HttpResponse(stereotype_vote.id)

    conversation = Conversation.objects.get(id=conversation_id)
    kwargs = conversation.get_url_kwargs()
    return redirect(reverse("boards:cluster-stereotype_votes", kwargs=kwargs))


def ctrl(request, conversation_id, slug, board_slug, check=check_promoted):
    conversation = Conversation.objects.get(id=conversation_id)
    check(conversation, request)
    user = request.user
    kwargs = conversation.get_url_kwargs()

    if request.method != "POST":
        return redirect(reverse("boards:cluster-index", kwargs=kwargs))
    if not user.has_perm("ej.can_edit_conversation", conversation):
        raise PermissionError("User cannot edit this conversation.")
    if request.POST["action"] == "force-clusterization":
        conversation.clusterization.update_clusterization(force=True)

    return redirect(reverse("boards:cluster-index", kwargs=kwargs))


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
            kwargs = conversation.get_url_kwargs()
            return redirect(reverse("boards:cluster-edit", kwargs=kwargs) + "?delete-success")
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


def get_json_shape_user_group_from_clusterization(clusterization, user):
    user_group = None
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
            if names:
                user_group = names[0]

    return {"json_data": shapes_json, "user_group": user_group, "clusters": clusters}
