import datetime
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncDay
from sidekick import import_later
from sidekick import property as property

from .comment import Comment
from .vote import VoteChannels

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
        "channel_votes": conversation.votes.aggregate(
            webchat=Count("channel", filter=Q(channel=VoteChannels.RASA_WEBCHAT)),
            telegram=Count("channel", filter=Q(channel=VoteChannels.TELEGRAM)),
            whatsapp=Count("channel", filter=Q(channel=VoteChannels.WHATSAPP)),
            opinion_component=Count("channel", filter=Q(channel=VoteChannels.OPINION_COMPONENT)),
            unknown=Count("channel", filter=Q(channel=VoteChannels.UNKNOWN)),
            ej=Count("channel", filter=Q(channel=VoteChannels.EJ)),
            rocketchat=Count("channel", filter=Q(channel=VoteChannels.ROCKETCHAT))
        ),
        "channel_participants": conversation.votes.aggregate(
            webchat=Count("author", filter=Q(channel=VoteChannels.RASA_WEBCHAT), distinct="author"),
            telegram=Count("author", filter=Q(channel=VoteChannels.TELEGRAM), distinct="author"),
            whatsapp=Count("author", filter=Q(channel=VoteChannels.WHATSAPP), distinct="author"),
            opinion_component=Count(
                "author", filter=Q(channel=VoteChannels.OPINION_COMPONENT), distinct="author"
            ),
            unknown=Count("author", filter=Q(channel=VoteChannels.UNKNOWN), distinct="author"),
            ej=Count("author", filter=Q(channel=VoteChannels.EJ), distinct="author"),
            rocketchat=Count("author", filter=Q(channel=VoteChannels.ROCKETCHAT), distinct="author")
        ),
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
        "total_comments": max_votes,
        "comments": given_votes + 1,
    }


def set_date_range(start_date, end_date):
    """
    Set all date range values ​​with 0.
    """
    date_range = end_date - start_date
    initial_values = [
        {"date": start_date + datetime.timedelta(days=i), "value": 0} for i in range(date_range.days + 1)
    ]
    return initial_values


def get_all_interval_dates(start_date, end_date, date_votes):
    initial_values = set_date_range(start_date, end_date)
    for data in date_votes:
        index = (data["date"] - start_date).days
        initial_values[index]["value"] = data["value"]
    return initial_values


def vote_distribution_over_time(conversation, start_date, end_date):
    """
    Returns the total votes for each day in a time interval.
    """
    # contains total votes only for days on which votes occurred.
    date_votes = conversation.votes.filter(
        created__range=(start_date, end_date + datetime.timedelta(days=1))
    )
    date_votes = (
        date_votes.annotate(date=TruncDay("created"))
        .values("date")
        .annotate(value=Count("id"))
        .order_by("-date")
    )
    return get_all_interval_dates(start_date, end_date, date_votes)
