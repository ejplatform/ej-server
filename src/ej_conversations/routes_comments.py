from hashlib import blake2b
from logging import getLogger

from boogie.router import Router
from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from . import models
from .enums import Choice

log = getLogger("ej")

app_name = "ej_conversations"
urlpatterns = Router(
    template="ej_conversations/comments/{name}.jinja2",
    models={"conversation": models.Conversation, "comment": models.Comment},
    login=True,
)
conversation_url = f"<model:conversation>/<slug:slug>/"


#
# Display conversations
#
@urlpatterns.route("<model:comment>-<hex_hash>/")
def detail(request, comment, hex_hash):
    if hex_hash != comment_url_hash(comment):
        raise Http404

    # We show an option for the user to vote, if it hasn't voted in the comment
    # or has skip it.
    user = request.user
    qs = models.Vote.objects.filter(comment=comment, author=user)
    if qs and qs.first().choice != Choice.SKIP:
        show_actions = False
        message = _(
            "You already voted in this comment as <strong>{vote}</strong>. "
            "You cannot change your vote."
        ).format(vote=qs.first().choice.description)
    elif request.method == "POST":
        vote = request.POST["vote"]
        comment.vote(user, vote)
        log.info(f"user {user.id} voted {vote} on comment {comment.id}")
        show_actions = False
        message = _("Your vote has been computed :-)")
    else:
        show_actions = True
        message = None

    return {
        "conversation": comment.conversation,
        "comment": comment,
        "message": message,
        "show_actions": show_actions,
    }


#
# Auxiliary functions
#
def comment_url(comment):
    return reverse(
        "comments:detail",
        kwargs={"comment": comment, "hex_hash": comment_url_hash(comment)},
    )


def comment_url_hash(comment):
    """
    Compute the URL hash for the given comment.
    """
    return blake2b(comment.content.encode("utf8"), digest_size=4).hexdigest()
