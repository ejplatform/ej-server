from boogie.rest import rest_api
from ej_conversations.models import Conversation


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


@rest_api.query_hook("ej_conversations.Vote")
def query_vote(request, qs):
    user = request.user
    if user.id:
        return qs.filter(author_id=user.id)
    return qs.none()
