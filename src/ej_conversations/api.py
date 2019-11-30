from boogie.rest import rest_api
from ej_conversations.models import Conversation
from ej_conversations.models.vote import Vote


#
# Conversation extra actions and attributes
#
@rest_api.action("ej_conversations.Conversation")
def vote_dataset(request, conversation):
    return conversation.votes.dataframe().to_dict(orient="list")


@rest_api.action("ej_conversations.Conversation")
def user_statistics(request, conversation):
    return conversation.statistics_for_user(request.user)


@rest_api.action("ej_conversations.Conversation")
def approved_comments(conversation):
    return conversation.comments.approved()


@rest_api.action("ej_conversations.Conversation")
def random_comment(request, conversation):
    return conversation.next_comment(request.user)


@rest_api.action("ej_conversations.Conversation", list=True)
def random(request):
    return Conversation.objects.random(request.user)


@rest_api.property("ej_conversations.Conversation")
def statistics(conversation):
    return conversation.statistics()


#
# Votes
#
@rest_api.save_hook("ej_conversations.Vote")
def save_vote(request, vote):
    user = request.user

    try:
        skipped_vote = Vote.objects.get(
            comment=vote.comment,
            choice=0,
            author=user)
        skipped_vote.choice = vote.choice
        skipped_vote.save()
        return skipped_vote
    except Exception as e:
        pass
    if vote.id is None:
        vote.author = user
        vote.save()
    elif vote.author != user:
        raise PermissionError("cannot update vote of a different user")
    else:
        vote.save(update_fields=["choice"])
    return vote


@rest_api.delete_hook("ej_conversations.Vote")
def delete_vote(request, vote):
    user = request.user

    if user.is_superuser:
        vote.delete()
    elif vote.author_id != user.id:
        raise PermissionError("cannot delete vote from another user")
    else:
        raise PermissionError("user is not allowed to delete votes")


def query_vote(request, qs):
    user = request.user
    if user.id:
        return qs.filter(author_id=user.id)
    return qs.none()


@rest_api.save_hook("ej_conversations.Comment")
def save_comment(request, comment):
    from ej_conversations.models.comment import Comment
    from rest_framework.authtoken.models import Token
    try:
        conversation_id = request.data.get('conversation')
        conversation = Conversation.objects.get(id=conversation_id)
        comment.author = request.user
        comment.conversation = conversation
        comment.save()
        return comment
    except Exception:
        raise PermissionError("could not create comment")
