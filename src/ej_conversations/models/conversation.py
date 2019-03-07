import hyperpython as hp
from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Count, Q
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from boogie import models
from boogie import rules
from boogie.rest import rest_api
from ej.utils.url import SafeUrl
from .comment import Comment
from .conversation_queryset import log, ConversationQuerySet
from .vote import Vote
from ..enums import Choice
from ..utils import normalize_status

NOT_GIVEN = object()


@rest_api(['title', 'text', 'author', 'slug', 'created'], lookup_field='slug')
class Conversation(TimeStampedModel):
    """
    A topic of conversation.
    """
    title = models.CharField(
        _('Title'),
        max_length=255,
        help_text=_(
            'Short description used to create URL slugs (e.g. School system).'
        ),
        unique=True,
    )
    text = models.TextField(
        _('Question'),
        help_text=_(
            'What do you want to ask?'
        ),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
        help_text=_(
            'Only the author and administrative staff can edit this conversation.'
        )
    )
    slug = AutoSlugField(
        unique=False,
        populate_from='title',
    )
    is_promoted = models.BooleanField(
        _('Promote conversation?'),
        default=False,
        help_text=_(
            'Promoted conversations appears in the main /conversations/ '
            'endpoint.'
        ),
    )
    is_hidden = models.BooleanField(
        _('Hide conversation?'),
        default=False,
        help_text=_(
            'Hidden conversations does not appears in boards or in the main /conversations/ '
            'endpoint.'
        ),
    )
    limit_report_users = models.PositiveIntegerField(
        _('Limit users'),
        default=0,
        help_text=_(
            'Limit number of participants, making /reports/ route unavailable if limit is reached '
            'except for super admin.'
        ),
    )

    objects = ConversationQuerySet.as_manager()
    tags = TaggableManager(through='ConversationTag')
    all_votes = property(lambda self: Vote.objects.filter(comment__conversation=self))
    votes = property(lambda self: self.all_votes.filter(comment__status=Comment.STATUS.approved))

    @property
    def users(self):
        return get_user_model().objects.filter(votes__in=self.votes).distinct()

    @property
    def approved_comments(self):
        return self.comments.filter(status=Comment.STATUS.approved)

    class Meta:
        ordering = ['created']
        permissions = (
            ('can_publish_promoted', _('Can publish promoted conversations')),
            ('is_moderator', _('Can moderate comments in any conversation')),
        )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.id is None:
            pass
        super().save(*args, **kwargs)

    def clean(self):
        can_edit = 'ej.can_edit_conversation'
        if self.is_promoted and self.author_id is not None and not self.author.has_perm(can_edit, self):
            raise ValidationError(_(
                'User does not have permission to create a promoted '
                'conversation.')
            )

    def get_absolute_url(self, board=None):
        kwargs = {'conversation': self, 'slug': self.slug}
        if board is None:
            board = getattr(self, 'board', None)
        if board:
            kwargs['board'] = board
            return SafeUrl('boards:conversation-detail', **kwargs)
        else:
            return SafeUrl('conversation:detail', **kwargs)

    def get_url(self, which, board=None, **kwargs):
        kwargs['conversation'] = self
        kwargs['slug'] = self.slug
        if board is None:
            board = getattr(self, 'board', None)
        if board:
            from ej_boards.models import BoardSubscription
            subscription = BoardSubscription.objects.filter(conversation=self)
            if subscription.exists():
                board = subscription[0].board
                kwargs['board'] = board
                which = 'boards:' + which.replace(':', '-')
                return SafeUrl(which, **kwargs)

        return SafeUrl(which, **kwargs)

    def get_anchor(self, name, which, **kwargs):
        return hp.a(name, href=self.get_url(which, **kwargs))

    def user_votes(self, user):
        """
        Get all votes in conversation for the given user.
        """
        if user.id is None:
            return Vote.objects.none()
        return self.votes.filter(author=user)

    def create_comment(self, author, content, commit=True, *, status=None,
                       check_limits=True, **kwargs):
        """
        Create a new comment object for the given user.

        If commit=True (default), comment is persisted on the database.

        By default, this method check if the user can post according to the
        limits imposed by the conversation. It also normalizes duplicate
        comments and reuse duplicates from the database.
        """

        # Convert status, if necessary
        if author.id == self.author.id:
            kwargs['status'] = Comment.STATUS.approved
        else:
            kwargs['status'] = normalize_status(status)

        # Check limits
        if check_limits and not author.has_perm('ej.can_comment', self):
            log.info('failed attempt to create comment by %s' % author)
            raise PermissionError('user cannot comment on conversation.')

        # Check if comment is created with rejected status
        if status == Comment.STATUS.rejected:
            msg = _('automatically rejected')
            kwargs.setdefault('rejection_reason', msg)

        kwargs.update(author=author, content=content.strip())
        comment = make_clean(Comment, commit, conversation=self, **kwargs)
        log.info('new comment: %s' % comment)
        return comment

    def vote_count(self, which=None):
        """
        Return the number of votes of a given type.
        """
        kwargs = {'comment__conversation_id': self.id}
        if which is not None:
            kwargs['choice'] = which
        return Vote.objects.filter(**kwargs).count()

    def statistics(self, cache=True):
        """
        Return a dictionary with basic statistics about conversation.
        """
        if cache:
            try:
                return self._cached_statistics
            except AttributeError:
                self._cached_statistics = self.statistics(False)
                return self._cached_statistics

        return {
            # Vote counts
            'votes': self.votes.aggregate(
                agree=Count('choice', filter=Q(choice=Choice.AGREE)),
                disagree=Count('choice', filter=Q(choice=Choice.DISAGREE)),
                skip=Count('choice', filter=Q(choice=Choice.SKIP)),
                total=Count('choice'),
            ),

            # Comment counts
            'comments': self.comments.aggregate(
                approved=Count('status', filter=Q(status=Comment.STATUS.approved)),
                rejected=Count('status', filter=Q(status=Comment.STATUS.rejected)),
                pending=Count('status', filter=Q(status=Comment.STATUS.pending)),
                total=Count('status'),
            ),

            # Participants count
            'participants': {
                'voters':
                    (get_user_model().objects
                        .filter(votes__comment__conversation_id=self.id)
                        .distinct()
                        .count()),
                'commenters':
                    (get_user_model().objects
                        .filter(comments__conversation_id=self.id,
                                comments__status=Comment.STATUS.approved)
                        .distinct()
                        .count()),
            },
        }

    def user_statistics(self, user):
        """
        Get information about user.
        """
        max_votes = \
            (self.comments
                .filter(status=Comment.STATUS.approved)
                .exclude(author_id=user.id)
                .count())
        given_votes = 0 if user.id is None else \
            (Vote.objects
                .filter(comment__conversation_id=self.id, author=user)
                .count())

        e = 1e-50  # for numerical stability
        return {
            'votes': given_votes,
            'missing_votes': max_votes - given_votes,
            'participation_ratio': given_votes / (max_votes + e),
        }

    def next_comment(self, user, default=NOT_GIVEN):
        """
        Returns a random comment that user didn't vote yet.

        If default value is not given, raises a Comment.DoesNotExit exception
        if no comments are available for user.
        """
        comment = rules.compute('ej_conversations.next_comment', self, user)
        if comment:
            return comment
        elif default is NOT_GIVEN:
            msg = _('No comments available for this user')
            raise Comment.DoesNotExist(msg)
        else:
            return default

    def is_favorite(self, user):
        """
        Checks if conversation is favorite for the given user.
        """
        return bool(self.favorites.filter(user=user).exists())

    def make_favorite(self, user):
        """
        Make conversation favorite for user.
        """
        self.favorites.update_or_create(user=user)

    def remove_favorite(self, user):
        """
        Remove favorite status for conversation
        """
        if self.is_favorite(user):
            self.favorites.filter(user=user).delete()

    def toggle_favorite(self, user):
        """
        Toggles favorite status of conversation.
        """
        try:
            self.favorites.get(user=user).delete()
        except ObjectDoesNotExist:
            self.make_favorite(user)


#
#  AUXILIARY MODELS
#
class ConversationTag(TaggedItemBase):
    """
    Add tags to Conversations with real Foreign Keys
    """
    content_object = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
    )


class FavoriteConversation(models.Model):
    """
    M2M relation from users to conversations.
    """
    conversation = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_conversations',
    )


#
# UTILITY FUNCTIONS
#
def make_clean(cls, commit=True, **kwargs):
    obj = cls(**kwargs)
    obj.full_clean()
    if commit:
        obj.save()
    return obj


def conversations_with_votes(user):
    return Conversation.objects.filter(comments__votes__author=user).distinct()


def patch_user_model(model):
    model.conversations_with_votes = property(conversations_with_votes)
