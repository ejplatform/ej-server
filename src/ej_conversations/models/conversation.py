from autoslug import AutoSlugField
from boogie import models
from boogie import rules
from boogie.rest import rest_api
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel
from sidekick import lazy, property as property, placeholder as this
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from ej.utils.functional import deprecate_lazy
from ej.utils.url import SafeUrl
from .comment import Comment
from .conversation_queryset import log, ConversationQuerySet
from .favorites import HasFavoriteMixin
from .util import make_clean
from .util import vote_count, statistics, statistics_for_user
from .vote import Vote
from ..enums import Choice
from ..signals import comment_moderated
from ..utils import normalize_status

from ej.components.menu import register_menu
from hyperpython import a

NOT_GIVEN = object()


@register_menu("conversations:detail-actions")
def conversation_links(request, conversation):
    return [
        a(_("Analysis"), href=conversation.url("conversation-analysis:index")),
        a(_("Tools"), href=conversation.url("conversation-tools:index")),
    ]


@rest_api(["title", "text", "author", "slug", "created"])
class Conversation(HasFavoriteMixin, TimeStampedModel):
    """
    A topic of conversation.
    """

    title = models.CharField(
        _("Title"),
        max_length=255,
        help_text=_("Short description used to create URL slugs (e.g. School system)."),
    )
    text = models.TextField(_("Question"), help_text=_("What do you want to ask?"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
        help_text=_("Only the author and administrative staff can edit this conversation."),
    )
    moderators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="moderated_conversations",
        help_text=_("Moderators can accept and reject comments."),
    )
    slug = AutoSlugField(unique=False, populate_from="title")
    is_promoted = models.BooleanField(
        _("Promote conversation?"),
        default=False,
        help_text=_("Promoted conversations appears in the main /conversations/ " "endpoint."),
    )
    is_hidden = models.BooleanField(
        _("Hide conversation?"),
        default=False,
        help_text=_(
            "Hidden conversations does not appears in boards or in the main /conversations/ " "endpoint."
        ),
    )

    objects = ConversationQuerySet.as_manager()
    tags = TaggableManager(through="ConversationTag", blank=True)
    votes = property(lambda self: Vote.objects.filter(comment__conversation=self))

    @property
    def users(self):
        return get_user_model().objects.filter(votes__comment__conversation=self).distinct()

    # Comment managers
    def _filter_comments(*args):
        *_, which = args
        status = getattr(Comment.STATUS, which)
        return property(lambda self: self.comments.filter(status=status))

    approved_comments = _filter_comments("approved")
    rejected_comments = _filter_comments("rejected")
    pending_comments = _filter_comments("pending")
    del _filter_comments

    class Meta:
        ordering = ["created"]
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        permissions = (
            ("can_publish_promoted", _("Can publish promoted conversations")),
            ("is_moderator", _("Can moderate comments in any conversation")),
        )

    #
    # Statistics and annotated values
    #
    author_name = lazy(this.author.name)
    first_tag = lazy(this.tags.values_list("name", flat=True).first())
    tag_names = lazy(this.tags.values_list("name", flat=True))

    # Statistics
    n_comments = deprecate_lazy(
        this.n_approved_comments, "Conversation.n_comments was deprecated in favor of .n_approved_comments."
    )
    n_approved_comments = lazy(this.approved_comments.count())
    n_pending_comments = lazy(this.pending_comments.count())
    n_rejected_comments = lazy(this.rejected_comments.count())
    n_total_comments = lazy(this.comments.count().count())

    n_favorites = lazy(this.favorites.count())
    n_tags = lazy(this.tags.count())
    n_votes = lazy(this.votes.count())
    n_final_votes = lazy(this.votes.exclude(choice=Choice.SKIP).count())
    n_participants = lazy(this.users.count())

    # Statistics for the request user
    user_comments = property(this.comments.filter(author=this.for_user))
    user_votes = property(this.votes.filter(author=this.for_user))
    n_user_total_comments = lazy(this.user_comments.count())
    n_user_comments = lazy(this.user_comments.filter(status=Comment.STATUS.approved).count())
    n_user_rejected_comments = lazy(this.user_comments.filter(status=Comment.STATUS.rejected).count())
    n_user_pending_comments = lazy(this.user_comments.filter(status=Comment.STATUS.pending).count())
    n_user_votes = lazy(this.user_votes.count())
    n_user_final_votes = lazy(this.user_votes.exclude(choice=Choice.SKIP).count())
    is_user_favorite = lazy(this.is_favorite(this.for_user))

    # Statistical methods
    vote_count = vote_count
    statistics = statistics
    statistics_for_user = statistics_for_user

    @lazy
    def for_user(self):
        return self.request.user

    @lazy
    def request(self):
        msg = "Set the request object by calling the .set_request(request) method first"
        raise RuntimeError(msg)

    # TODO: move as patches from other apps
    @lazy
    def n_clusters(self):
        try:
            return self.clusterization.n_clusters
        except AttributeError:
            return 0

    @lazy
    def n_stereotypes(self):
        try:
            return self.clusterization.n_clusters
        except AttributeError:
            return 0

    n_endorsements = 0  # FIXME: endorsements

    def __str__(self):
        return self.title

    def set_request(self, request_or_user):
        """
        Saves optional user and request attributes in model. Those attributes are
        used to compute and cache many other attributes and statistics in the
        conversation model instance.
        """
        request = None
        user = request_or_user
        if not isinstance(request_or_user, get_user_model()):
            user = request_or_user.user
            request = request_or_user

        if self.__dict__.get("for_user", user) != user or self.__dict__.get("request", request) != request:
            raise ValueError("user/request already set in conversation!")

        self.for_user = user
        self.request = request

    def save(self, *args, **kwargs):
        if self.id is None:
            pass
        super().save(*args, **kwargs)

    def clean(self):
        can_edit = "ej.can_edit_conversation"
        if self.is_promoted and self.author_id is not None and not self.author.has_perm(can_edit, self):
            raise ValidationError(_("User does not have permission to create a promoted " "conversation."))

    def get_absolute_url(self, board=None):
        kwargs = {"conversation": self, "slug": self.slug}
        if board is None:
            board = getattr(self, "board", None)
        if board:
            kwargs["board"] = board
            return SafeUrl("boards:conversation-detail", **kwargs)
        else:
            return SafeUrl("conversation:detail", **kwargs)

    def url(self, which="conversation:detail", board=None, **kwargs):
        """
        Return a url pertaining to the current conversation.
        """
        if board is None:
            board = getattr(self, "board", None)

        kwargs["conversation"] = self
        kwargs["slug"] = self.slug

        if board:
            kwargs["board"] = board
            which = "boards:" + which.replace(":", "-")
            return SafeUrl(which, **kwargs)

        return SafeUrl(which, **kwargs)

    def votes_for_user(self, user):
        """
        Get all votes in conversation for the given user.
        """
        if user.id is None:
            return Vote.objects.none()
        return self.votes.filter(author=user)

    def create_comment(self, author, content, commit=True, *, status=None, check_limits=True, **kwargs):
        """
        Create a new comment object for the given user.

        If commit=True (default), comment is persisted on the database.

        By default, this method check if the user can post according to the
        limits imposed by the conversation. It also normalizes duplicate
        comments and reuse duplicates from the database.
        """

        # Convert status, if necessary
        if status is None and (
            author.id == self.author.id or author.has_perm("ej.can_edit_conversation", self)
        ):
            kwargs["status"] = Comment.STATUS.approved

        else:
            kwargs["status"] = normalize_status(status)

        # Check limits
        if check_limits and not author.has_perm("ej.can_comment", self):
            log.info("failed attempt to create comment by %s" % author)
            raise PermissionError("user cannot comment on conversation.")

        # Check if comment is created with rejected status
        if status == Comment.STATUS.rejected:
            msg = _("automatically rejected")
            kwargs.setdefault("rejection_reason", msg)

        kwargs.update(author=author, content=content.strip())
        comment = make_clean(Comment, commit, conversation=self, **kwargs)
        if comment.status == comment.STATUS.approved and author != self.author:
            comment_moderated.send(
                Comment,
                comment=comment,
                moderator=comment.moderator,
                is_approved=True,
                author=comment.author,
            )
        log.info("new comment: %s" % comment)
        return comment

    def next_comment(self, user, default=NOT_GIVEN):
        """
        Returns a random comment that user didn't vote yet.

        If default value is not given, raises a Comment.DoesNotExit exception
        if no comments are available for user.
        """
        comment = rules.compute("ej.next_comment", self, user)
        if comment:
            return comment
        return None

    def next_comment_with_id(self, user, comment_id=None):
        """
        Returns a comment with id if user didn't vote yet, otherwhise return
        a random comment.
        """
        if comment_id:
            try:
                return self.approved_comments.exclude(votes__author=user).get(id=comment_id)
            except Exception as e:
                pass
        return self.next_comment(user)


#
#  AUXILIARY MODELS
#
class ConversationTag(TaggedItemBase):
    """
    Add tags to Conversations with real Foreign Keys
    """

    content_object = models.ForeignKey("Conversation", on_delete=models.CASCADE)
