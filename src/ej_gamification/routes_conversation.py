from boogie.router import Router
from django.utils import timezone

from ej_conversations.models import Conversation
from ej_conversations.utils import check_promoted
from ej_gamification.models import endorse_comment
from ej_gamification.models.progress import get_participation, get_progress

app_name = "ej_gamification"
urlpatterns = Router(
    template="ej_gamification/conversation/{name}.jinja2",
    base_path="<model:conversation>/<slug:slug>/",
    models={"conversation": Conversation},
    login=True,
)


@urlpatterns.route("achievements/")
def achievements(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user

    return {
        "user": user,
        "progress": get_participation(user, conversation),
        "conversation_progress": get_progress(conversation),
    }


@urlpatterns.route("endorse-comments/", perms=["ej.can_edit_conversation"])
def endorse(request, conversation, slug, check=check_promoted):
    check(conversation, request)
    user = request.user
    comments = list(
        conversation.comments.approved().exclude(
            endorsements__is_global=True, endorsements__end__gte=timezone.now()
        )
    )

    if request.method == "POST":
        comment_ids = _fetch_list_of_comments_ids_from_post(request.POST)
        _endorse_comment_in_list(comments, comment_ids, request.user)

    return {"user": user, "conversation": conversation, "comments": comments}


def _fetch_list_of_comments_ids_from_post(data):
    comment_ids = set()
    for k, v in data.items():
        if k.startswith("endorse-") and v == "on":
            k = int(k.partition("-")[2])
            comment_ids.add(k)
    return comment_ids


def _endorse_comment_in_list(comments, which, author):
    id_map = {comment.id: comment for comment in comments}

    for comment_id in which:
        try:
            comment = id_map[comment_id]
        except KeyError:
            raise PermissionError()
        endorse_comment(comment, author=author)
