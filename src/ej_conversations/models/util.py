from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from sidekick import import_later
from sidekick import property as property

from .comment import Comment

models = import_later("ej_conversations.models")


def make_clean(cls, commit=True, **kwargs):
    """
    Create an instance of the cls model (or execute the cls callable) and
    call the resulting object .full_clean() method and later decide to save it
    (if commit=True) or not.
    """

    obj = cls(**kwargs)
    obj.full_clean()
    if commit:
        obj.save()
    return obj


def patch_user_model(model):
    def conversations_with_votes(user):
        return models.Conversation.objects.filter(comments__votes__author=user).distinct()

    model.conversations_with_votes = property(conversations_with_votes)


#
# Conversation statistics
#
def vote_count(conversation, which=None):
    """
    Return the number of votes of a given type.
    """
    kwargs = {"comment__conversation_id": conversation.id}
    if which is not None:
        kwargs["choice"] = which
    return models.Vote.objects.filter(**kwargs).count()


def statistics(conversation, cache=True):
    """
    Return a dictionary with basic statistics about conversation.
    """
    if cache:
        try:
            return conversation._cached_statistics
        except AttributeError:
            conversation._cached_statistics = conversation.statistics(False)
            return conversation._cached_statistics

    return {
        # Vote counts
        "votes": conversation.votes.aggregate(
            agree=Count("choice", filter=Q(choice=models.Choice.AGREE)),
            disagree=Count("choice", filter=Q(choice=models.Choice.DISAGREE)),
            skip=Count("choice", filter=Q(choice=models.Choice.SKIP)),
            total=Count("choice"),
        ),
        # Comment counts
        "comments": conversation.comments.aggregate(
            approved=Count("status", filter=Q(status=models.Comment.STATUS.approved)),
            rejected=Count("status", filter=Q(status=models.Comment.STATUS.rejected)),
            pending=Count("status", filter=Q(status=models.Comment.STATUS.pending)),
            total=Count("status"),
        ),
        # Participants count
        "participants": {
            "voters": (
                get_user_model()
                .objects.filter(votes__comment__conversation_id=conversation.id)
                .distinct()
                .count()
            ),
            "commenters": (
                get_user_model()
                .objects.filter(
                    comments__conversation_id=conversation.id, comments__status=Comment.STATUS.approved
                )
                .distinct()
                .count()
            ),
        },
    }


def statistics_for_user(conversation, user):
    """
    Get information about user.
    """
    max_votes = conversation.comments.filter(status=Comment.STATUS.approved).count()
    given_votes = (
        0
        if user.id is None
        else (
            models.Vote.objects.filter(comment__conversation_id=conversation.id, author=user)
            .exclude(choice=0)
            .count()
        )
    )

    e = 1e-50  # for numerical stability
    return {
        "votes": given_votes,
        "missing_votes": max_votes - given_votes,
        "participation_ratio": given_votes / (max_votes + e),
    }
