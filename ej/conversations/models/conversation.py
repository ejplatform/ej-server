from random import randrange

import datetime
from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.timezone import make_aware, get_current_timezone
from django.utils.translation import ugettext_lazy as _

from .category import Category
from .comment import Comment
from .utils import custom_slugify, NUDGE
from .vote import Vote
from ..validators import validate_color

User = get_user_model()
NOT_GIVEN = object()


class Conversation(models.Model):
    """
    Describes a conversation.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    title = models.CharField(
        _('Title'),
        max_length=255,
        blank=False,
    )
    description = models.TextField(
        _('Description'),
        blank=False,
    )
    dialog = models.TextField(
        _('Dialog'),
        null=True, blank=True,
    )
    response = models.TextField(
        _('Response'),
        null=True, blank=True,
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True,
    )
    position = models.IntegerField(
        _('Position'),
        null=True, blank=True,
        default=0,
    )
    is_new = models.BooleanField(
        _('Is new'),
        default=True,
    )
    slug = AutoSlugField(
        null=True,
        default=None,
        unique=True,
        populate_from='title',
        slugify=custom_slugify,
    )
    opinion = models.TextField(
        _('Our Opinion'),
        null=True, blank=True,
    )
    promoted = models.BooleanField(
        _('Promoted'),
        default=False,
    )
    category = models.ForeignKey(
        Category,
        related_name='conversations',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    background_image = models.ImageField(
        _('Background image'),
        upload_to='conversations/backgrounds',
        null=True, blank=True,
    )
    background_color = models.CharField(
        _('Background color'),
        max_length=7,
        validators=[validate_color],
        null=True, blank=True,
    )
    # Nudge configuration
    comment_nudge = models.IntegerField(
        _('Comment nudge'),
        null=True, blank=True,
        help_text=_('Number of comments'),
    )
    comment_nudge_interval = models.IntegerField(
        _('Comment nudge interval'),
        null=True, blank=True,
        help_text=_('Nudge interval in seconds'),
    )
    comment_nudge_global_limit = models.IntegerField(
        _('Comment nudge global limit'),
        null=True, blank=True,
        help_text=_('Global number of comments'),
    )

    class Meta:
        ordering = ('created_at',)

    # Statistics configuration
    # you can override this variable in django settings variable MATH_REFRESH_TIME
    # passing a integer value in seconds
    STATISTICS_REFRESH_TIME = getattr(settings, 'CONVERSATION_STATISTICS_REFRESH_TIME', 0)
    NUDGE = NUDGE

    # Vote count
    agree_votes = property(lambda self: vote_count(self, Vote.AGREE))
    disagree_votes = property(lambda self: vote_count(self, Vote.DISAGREE))
    pass_votes = property(lambda self: vote_count(self, Vote.PASS))
    total_votes = property(lambda self: vote_count(self))

    # Comment count
    approved_comments = property(lambda self: comment_count(self, Comment.APPROVED))
    rejected_comments = property(lambda self: comment_count(self, Comment.REJECTED))
    unmoderated_comments = property(lambda self: comment_count(self, Comment.PENDING))
    total_comments = property(lambda self: comment_count(self))

    # Category properties
    category_name = property(lambda self: self.category.name)
    category_customizations = property(lambda self: self.category.customizations)
    category_slug = property(lambda self: self.category.slug)

    @property
    def total_participants(self):
        return (
            User.objects
                .filter(votes__comment__conversation_id=self.id)
                .distinct()
                .count()
        )

    @property
    def participation_clusters(self):
        from ej.math.models import Job
        return (
            self.math_jobs
                .filter(type=Job.CLUSTERS, status=Job.FINISHED)
                .order_by('created_at')
                .last()
        )

    def __str__(self):
        return self.title

    def create_comment(self, author, content, commit=True, check_limits=True,
                       **kwargs):
        """
        Create a new comment object for the given user.

        By default, this method checks if user is within the throttle limits
        for comment publication.
        """
        make_comment = Comment.objects.create if commit else Comment
        return make_comment(author=author, content=content, **kwargs)

    def get_absolute_url(self):
        return '/conversations/' + self.slug

    def get_user_participation_ratio(self, user):
        """
        Ratio between "given votes" / "possible votes"
        """
        comments = (
            self.comments
                .filter(approval=Comment.APPROVED)
                .exclude(author=user)
                .count()
        )
        if not comments:
            return 0
        else:
            votes = (
                Vote.objects
                    .filter(comment__conversation_id=self.id, author=user)
                    .count()
            )
            return votes / comments

    def get_random_unvoted_comment(self, user, default=NOT_GIVEN):
        """
        Returns a random comment that user didn't vote yet.

        If default value is not given, raise an exception if no comments are available for user.
        """
        unvoted_comments = self.comments.filter(
            ~Q(author_id=user.id),
            ~Q(votes__author_id=user.id),
            approval=Comment.APPROVED,
        )
        size = unvoted_comments.count()
        if size:
            return unvoted_comments[randrange(0, size)]
        elif default is not NOT_GIVEN:
            return default
        else:
            msg = _('There is no comments available for this user')
            raise Comment.DoesNotExist(msg)

    def get_nudge_status(self, user):
        """
        Verify specific user nudge status in a conversation
        """
        if user:
            if is_user_nudge_global_limit_blocked(self, user):
                return self.NUDGE.global_blocked
            if self.comment_nudge and self.comment_nudge_interval:
                user_comments = get_nudge_interval_comments(self, user)
                user_comments_counter = user_comments.count()

                if is_user_nudge_interval_blocked(self, user_comments_counter):
                    return self.NUDGE.interval_blocked
                elif is_user_nudge_eager(self, user_comments_counter, user_comments):
                    return self.NUDGE.eager
            return self.NUDGE.normal
        else:
            raise User.DoesNotExist(_('User not found'))

    def update_statistics(self):
        """
        Creates a Job to update the clusters of users
        """
        if can_update_statistics(self):
            self.math_jobs.create(type="CLUSTERS")

    def list_votes(self):
        """
        Return a list of (value, author, comment) for each vote cast in
        the conversation.
        """
        return list(
            Vote.objects
                .filter(comment__conversation_id=self.id)
                .values_list('value', 'author_id', 'comment_id')
        )


#
# Utility functions.
# In the future we want to convert most of these to Django-rules.
#
def can_update_statistics(conversation, statistics_refresh_time=None):
    """
    Statistics can be updated when the last math job created respect the
    time limit defined by the MATH_REFRESH_TIME django settings variable.
    This time can be overridden by passing as argument a integer time value
    in seconds to this method.
    """
    if statistics_refresh_time is None:
        statistics_refresh_time = Conversation.STATISTICS_REFRESH_TIME

    math_refresh_limit = get_datetime_interval(statistics_refresh_time)
    jobs_in_limit = conversation.math_jobs.filter(created_at__gt=math_refresh_limit)
    return not jobs_in_limit


def get_datetime_interval(interval, datetime_reference=None):
    """
    Returns the the datetime_reference past interval
    interval param should be in seconds
    """
    if not datetime_reference:
        datetime_reference = datetime.datetime.now()

    timedelta = datetime.timedelta(seconds=interval)
    time_limit = datetime_reference - timedelta
    return make_aware(time_limit, get_current_timezone())


def get_nudge_interval_comments(conversation, user):
    """
    Returns how many comments user has between now and past
    comment_nudge_interval
    """
    nudge_interval_comments = []
    nudge_interval = conversation.comment_nudge_interval
    if nudge_interval:
        datetime_limit = get_datetime_interval(nudge_interval)
        nudge_interval_comments = user.comments.filter(
            created_at__gt=datetime_limit,
            conversation_id=conversation.id)
    return nudge_interval_comments


def is_user_nudge_global_limit_blocked(conversation, user):
    """
    Check number of user's comments is lower than the global limit
    """
    if conversation.comment_nudge_global_limit:
        user_comments_counter = user.comments.filter(
            conversation_id=conversation.id).count()
        return user_comments_counter >= conversation.comment_nudge_global_limit
    else:
        return False


def is_user_nudge_interval_blocked(conversation, user_comments_counter):
    """
    User cannot write too many comments. The limit is set by the
    conversation's comment_nudge and comment_nudge_interval
    """
    if conversation.comment_nudge:
        return user_comments_counter >= conversation.comment_nudge
    else:
        return False


def is_user_nudge_eager(conversation, user_comments_counter, user_comments):
    """
    A user is an eager user when he creates half of the comments that
    is possible in the middle of the nudge interval
    """
    if conversation.comment_nudge and conversation.comment_nudge_interval:
        nudge_limit = conversation.comment_nudge - 1
        if user_comments_counter >= nudge_limit:
            datetime_limit = get_datetime_interval(conversation.comment_nudge_interval)
            comments_in_limit = user_comments.filter(created_at__gt=datetime_limit)
            return comments_in_limit.count() >= nudge_limit
    return False


def vote_count(conversation, type=None):
    """
    Return the number of votes of a given type

    ``type=None`` for all votes.
    """

    kwargs = {'value': type} if type is not None else {}
    return (
        Vote.objects
            .filter(comment__conversation_id=conversation.id, **kwargs)
            .count()
    )


def comment_count(conversation, type=None):
    """
    Return the number of comments of a given type.

    ``type=None`` for all comments.
    """

    kwargs = {'approval': type} if type is not None else {}
    return conversation.comments.filter(**kwargs).count()
