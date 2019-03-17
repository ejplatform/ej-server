from boogie import models
from django.conf import settings
from django.utils.translation import ugettext as __, ugettext_lazy as _
from sidekick import delegate_to, lazy, import_later, placeholder as this

from ..enums import CommenterLevel, HostLevel, ProfileLevel, ConversationLevel, VoterLevel

signals = import_later('..signals', package=__package__)


class ProgressBase(models.Model):
    """
    Common features of all Progress models.
    """
    score = models.PositiveSmallIntegerField(
        default=0,
    )
    score_bias = models.SmallIntegerField(
        default=0,
    )

    @classmethod
    def level_fields(cls):
        try:
            return cls.__dict__['_level_fields']
        except KeyError:
            fields = {}
            for field in cls._meta.fields:
                if field.name.endswith('_level') and not field.name.startswith('max_'):
                    fields[field.name[:-6]] = field.enum
            setattr(cls, '_level_fields', fields)
            return fields

    @property
    def level_achievement_signal(self):
        raise NotImplementedError('must be defined in subclass')

    class Meta:
        abstract = True

    def sync(self):
        self.score = self.compute_score()
        self.update_levels(commit=False)
        return self

    def update_level(self, name, commit=True):
        """
        Update given level and possibly save modification, if necessary.

        Return True, if level was changed and False otherwise.
        """
        level_attr = name + '_level'
        max_level_attr = f'max_{name}_level'

        current = getattr(self, level_attr)
        new_level = current.check_level(self)
        max_level = getattr(self, max_level_attr)

        if new_level != current:
            update_fields = [level_attr]
            setattr(self, level_attr, new_level)
            if new_level > max_level:
                setattr(self, max_level_attr, new_level)
                update_fields.append(max_level_attr)

            self.notify_achievement(new_level, name, new_level > current)

            if commit:
                self.save(update_fields=update_fields)
            return True

        return False

    def update_levels(self, commit=True):
        """
        Update all levels in model.

        Return a list with all updated levels.
        """

        updated = []
        for name in self.level_fields():
            if self.update_level(name, commit=False):
                updated.append(name)

        if commit and updated:
            fields = [
                *(f'{name}_level' for name in updated),
                *(f'max_{name}_level' for name in updated),
            ]
            self.save(update_fields=fields)

        return updated

    def compute_score(self):
        """
        Return score computed from user achievements.
        """
        raise NotImplementedError('must be implemented in subclass')

    def notify_achievement(self, level, track, is_improvement):
        """
        Send the proper signal to notify a new user achievement.
        """
        signal = self.level_achievement_signal
        args = {
            'progress': self,
            'level': level,
            'track': track,
            'is_improvement': is_improvement,
        }
        if 'user' in signal.providing_args:
            args['user'] = self.user
        if 'conversation' in signal.providing_args:
            args['conversation'] = self.conversation
        return signal.send_robust(type(self), **args)


class UserProgress(ProgressBase):
    """
    Tracks global user evolution.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='progress',
        on_delete=models.CASCADE,
    )
    commenter_level = models.EnumField(
        CommenterLevel,
        default=CommenterLevel.NONE,
    )
    max_commenter_level = models.EnumField(
        CommenterLevel,
        default=CommenterLevel.NONE,
    )
    host_level = models.EnumField(
        HostLevel,
        default=HostLevel.NONE,
    )
    max_host_level = models.EnumField(
        HostLevel,
        default=HostLevel.NONE,
    )
    profile_level = models.EnumField(
        ProfileLevel,
        default=ProfileLevel.NONE,
    )
    max_profile_level = models.EnumField(
        ProfileLevel,
        default=ProfileLevel.NONE,
    )

    # Non de-normalized fields: conversations app
    n_conversations = delegate_to('user')
    n_comments = delegate_to('user')
    n_rejected_comments = delegate_to('user')
    n_votes = delegate_to('user')

    # Gamification app
    n_endorsements = delegate_to('user')
    n_given_opinion_bridge_powers = delegate_to('user')
    n_given_minority_activist_powers = delegate_to('user')

    # Level of conversations
    def _level_checker(*args):
        *_, lvl = args  # ugly trick to make static analysis happy
        return lazy(lambda p: p.user.conversations
                    .filter(progress__conversation_level=lvl)
                    .count())

    n_conversation_lvl_1 = _level_checker(ConversationLevel.ALIVE)
    n_conversation_lvl_2 = _level_checker(ConversationLevel.ENGAGING)
    n_conversation_lvl_3 = _level_checker(ConversationLevel.NOTEWORTHY)
    n_conversation_lvl_4 = _level_checker(ConversationLevel.ENGAGING)
    del _level_checker

    # Aggregators
    total_conversation_score = delegate_to('user')
    total_participation_score = delegate_to('user')

    # Signals
    level_achievement_signal = lazy(lambda _: signals.user_level_achieved, shared=True)

    class Meta:
        verbose_name_plural = _('User progress list')

    def __str__(self):
        return __('Progress for {user}').format(user=self.user)

    def compute_score(self):
        """
        Compute the total number of points earned by user.

        User score is based on the following rules:
            * Vote: 10 points
            * Accepted comment: 30 points
            * Rejected comment: -30 points
            * Endorsement received: 15 points
            * Opinion bridge: 50 points
            * Minority activist: 50 points
            * Plus the total score of created conversations.

        Returns:
            Total score (int)
        """
        return (
            self.score_bias
            + 10 * self.n_votes
            + 30 * self.n_comments
            - 30 * self.n_rejected_comments
            + 15 * self.n_endorsements
            + 50 * self.n_given_opinion_bridge_powers
            + 50 * self.n_given_minority_activist_powers
            + self.total_conversation_score
        )


class ConversationProgress(ProgressBase):
    """
    Tracks activity in conversation.
    """

    conversation = models.OneToOneField(
        'ej_conversations.Conversation',
        related_name='progress',
        on_delete=models.CASCADE,
    )
    conversation_level = models.EnumField(
        ConversationLevel,
        default=CommenterLevel.NONE,
    )
    max_conversation_level = models.EnumField(
        ConversationLevel,
        default=CommenterLevel.NONE,
    )

    # Non de-normalized fields: conversations
    n_votes = delegate_to('conversation')
    n_comments = delegate_to('conversation')
    n_rejected_comments = delegate_to('conversation')
    n_participants = delegate_to('conversation')
    n_favorites = delegate_to('conversation')
    n_tags = delegate_to('conversation')

    # Clusterization
    n_clusters = delegate_to('conversation')
    n_stereotypes = delegate_to('conversation')

    # Gamification
    n_endorsements = delegate_to('conversation')

    # Signals
    level_achievement_signal = lazy(lambda _: signals.conversation_level_achieved, shared=True)

    class Meta:
        verbose_name_plural = _('Conversation progress list')

    def __str__(self):
        return __('Progress for "{conversation}"').format(conversation=self.conversation)

    def compute_score(self):
        """
        Compute the total number of points for user contribution.

        Conversation score is based on the following rules:
            * Vote: 1 points
            * Accepted comment: 2 points
            * Rejected comment: -3 points
            * Endorsement created: 3 points

        Returns:
            Total score (int)
        """
        return (
            self.score_bias
            + self.n_votes
            + 2 * self.n_comments
            - 3 * self.n_rejected_comments
            + 3 * self.n_endorsements
        )


class ParticipationProgress(ProgressBase):
    """
    Tracks user evolution in conversation.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='participation_progresses',
        on_delete=models.CASCADE,
    )
    conversation = models.ForeignKey(
        'ej_conversations.Conversation',
        related_name='participation_progresses',
        on_delete=models.CASCADE,
    )
    voter_level = models.EnumField(
        VoterLevel,
        default=VoterLevel.NONE,
    )
    max_voter_level = models.EnumField(
        VoterLevel,
        default=VoterLevel.NONE,
    )
    is_owner = models.BooleanField(default=False)
    is_focused = models.BooleanField(default=False)

    # Non de-normalized fields: conversations
    is_favorite = lazy(lambda p: p.conversation.favorites.filter(user=p.user).exists())
    n_votes = lazy(lambda p: p.user.votes.filter(comment__conversation=p.conversation).count())
    n_comments = lazy(lambda p: p.user.comments.filter(conversation=p.conversation).count())
    n_rejected_comments = lazy(
        lambda p: p.user.rejected_comments.filter(conversation=p.conversation).count())
    n_conversation_comments = delegate_to('conversation', name='n_comments')
    n_conversation_rejected_comments = delegate_to('conversation', name='n_rejected_comments')
    votes_ratio = lazy(this.n_votes / (this.n_conversation_comments + 1e-50))

    # Gamification
    # n_endorsements = lazy(lambda p: Endorsement.objects.filter(comment__author=p.user).count())
    # n_given_opinion_bridge_powers = delegate_to('user')
    # n_given_minority_activist_powers = delegate_to('user')
    n_endorsements = 0
    n_given_opinion_bridge_powers = 0
    n_given_minority_activist_powers = 0

    # Leaderboard
    @lazy
    def n_conversation_scores(self):
        db = ParticipationProgress.objects
        return db.filter(conversation=self.conversation).count()

    @lazy
    def n_higher_scores(self):
        db = ParticipationProgress.objects
        return db.filter(conversation=self.conversation, score__gt=self.score).count()

    n_lower_scores = lazy(this.n_conversation_scores - this.n_higher_scores)

    # Signals
    level_achievement_signal = lazy(lambda _: signals.participation_level_achieved, shared=True)

    def __str__(self):
        msg = __('Progress for user: {user} at {conversation}')
        return msg.format(user=self.user, conversation=self.conversation)

    def sync(self):
        self.is_owner = self.conversation.author == self.user

        # You cannot receive a focused achievement in your own conversation!
        if not self.is_owner:
            n_comments = self.conversation.n_comments
            self.is_focused = n_comments == self.n_votes >= 20

        return super().sync()

    def compute_score(self):
        """
        Compute the total number of points earned by user.

        User score is based on the following rules:
            * Vote: 10 points
            * Accepted comment: 30 points
            * Rejected comment: -30 points
            * Endorsement received: 15 points
            * Opinion bridge: 50 points
            * Minority activist: 50 points
            * Plus the total score of created conversations.
            * Got a focused badge: 50 points.

        Returns:
            Total score (int)
        """
        return (
            self.score_bias
            + 10 * self.n_votes
            + 30 * self.n_comments
            - 30 * self.n_rejected_comments
            + 15 * self.n_endorsements
            + 50 * self.n_given_opinion_bridge_powers
            + 50 * self.n_given_minority_activist_powers
            + 50 * self.is_focused
        )
