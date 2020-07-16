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
def user_comments(request, conversation):
    return conversation.comments.filter(author=request.user)


@rest_api.action("ej_conversations.Conversation")
def user_pending_comments(request, conversation):
    return conversation.comments.filter(status='pending', author=request.user)


@rest_api.action("ej_conversations.Conversation")
def random_comment(request, conversation):
    return conversation.next_comment(request.user)


@rest_api.action("ej_conversations.Conversation", list=True)
def random(request):
    return Conversation.objects.random(request.user)


@rest_api.property("ej_conversations.Conversation")
def statistics(conversation):
    return conversation.statistics()


# This action will only works if the header 'accept=text/csv' is present on the request.
@rest_api.action("ej_conversations.Conversation")
def reports(request, conversation):
    from ej_dataviz.routes_report import comments_data_common, vote_data_common, cluster_data_common
    fmt = request.GET.get('fmt')
    data_to_export = request.GET.get('export')
    filename = conversation.slug + "-" + data_to_export
    EXPORT_QUERY = {
        "votes": conversation.votes,
        "comments": conversation.comments,
        "clusters": conversation.clusters
    }
    query = EXPORT_QUERY[data_to_export]
    if data_to_export == 'votes':
        return vote_data_common(query, filename, fmt)
    if data_to_export == 'clusters':
        return cluster_data_common(query, conversation.comments, conversation.votes,  filename, fmt)
    return comments_data_common(query, None, filename, fmt)


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
        comment.status = 'pending'
        comment.save()
        return comment
    except Exception:
        raise PermissionError("could not create comment")
