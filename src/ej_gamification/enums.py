from collections import namedtuple
from math import ceil, sqrt

from boogie.fields import IntEnum
from django.utils.translation import ugettext_lazy as _, ugettext as __, ngettext

from ej_profiles.enums import Gender, Race
from ej_profiles.forms import EDITABLE_FIELDS as PROFILE_EDITABLE_FIELDS
from ej_profiles.models import get_profile


class LevelMixin:
    """
    Basic abstract interface to all Level track enums.

    They all have a few properties in common:

        * The minimum interface defined by this class
        * Start at the first level NONE, represented as zero.
        * Have four more levels afterwards.
    """

    @classmethod
    def check_level(cls, data):
        """
        Checks the level from arguments.
        """
        raise NotImplementedError

    @classmethod
    def skipping_none(cls):
        it = iter(cls)
        next(it)
        yield from it

    def achieve_next_level_msg(self, data):
        """
        Message that explains what user needs to do to achieve the next level.
        """
        raise NotImplementedError


# ==============================================================================
# Levels that consume UserProgress information and track global user progress
# ------------------------------------------------------------------------------


class CommenterLevel(LevelMixin, IntEnum):
    """
    COMMENTER TRACK

    Keeps track of the total number of accepted comments. User generally have
    to participate in many different conversation to achieve higher ranks in
    this track.

    The test function receives an instance of UserProgress.
    """

    NONE = 0, _("No level")
    SHY = 1, _("Shy")
    PARTICIPATIVE = 2, _("Participative")
    OUTSPOKEN = 3, _("Outspoken")
    VOCAL = 4, _("Vocal")

    @classmethod
    def _levels(cls):
        return [5, 15, 45, 150]

    @classmethod
    def score(cls, data):
        n = data.n_approved_comments
        m = data.n_endorsements
        return n + m / 2

    @classmethod
    def check_level(cls, data):
        score = cls.score(data)
        level = cls.NONE
        for lvl, points in zip(cls.skipping_none(), cls._levels()):
            if score >= points:
                level = lvl
        return level

    def achieve_next_level_msg(self, data):
        required_score = self._levels()[self.value] - self.score(data)
        n = ceil(required_score)
        m = ceil(2 * required_score)
        msg = _("You need to publish {n} new comments or receive {m} new endorsements")
        return msg.format(n=n, m=m)


class HostLevel(LevelMixin, IntEnum):
    """
    HOST TRACK

    Keeps track of relevant conversations created by user. Users evolve in this
    track by having created conversations achieving good scores in their
    respective host level tracks.

    The test function receives an instance of UserProgress.
    """

    NONE = 0, _("No level")
    CHAPERON = 1, _("Chaperon")
    INFLUENCER = 2, _("Influencer")
    LEADER = 3, _("Leader")
    AUTHORITY = 4, _("Authority")

    @classmethod
    def _levels(cls):
        return [(2, 0, 0, 0), (4, 2, 0, 0), (8, 3, 1, 0), (16, 8, 3, 1)]

    @classmethod
    def check_level(cls, data):
        level = cls.NONE
        for lvl, (a, b, c, d) in zip(cls.skipping_none(), cls._levels()):
            lvl4 = data.n_conversation_lvl_4
            lvl3 = data.n_conversation_lvl_3
            lvl2 = data.n_conversation_lvl_2
            lvl1 = data.n_conversation_lvl_1
            if lvl4 >= d and lvl3 >= c and lvl2 >= b and lvl1 >= a:
                level = lvl
        return level

    def achieve_next_level_msg(self, data):
        if self is self.AUTHORITY:
            return _("Congratulations! You reached the maximum level")

        a, b, c, d = self._levels()[self.value]

        lvl4 = data.n_conversation_lvl_4
        if d and d > lvl4:
            n = d - lvl4
            return ngettext(
                "You need at least one more conversation at level 4",
                "You need at least {n} level 4 conversations",
                n,
            ).format(n=n)

        lvl3 = data.n_conversation_lvl_3 + lvl4
        if c and c > lvl3:
            n = c - lvl3
            return ngettext(
                "You need at least one more conversation at level 3",
                "You need at least {n} level 3 conversations",
                n,
            ).format(n=n)

        lvl2 = data.n_conversation_lvl_2 + lvl3
        if b and b > lvl2:
            n = b - lvl2
            return ngettext(
                "You need at least one more conversation at level 2",
                "You need at least {n} level 2 conversations",
                n,
            ).format(n=n)

        lvl1 = data.n_conversation_lvl_1 + lvl2
        n = a - lvl1
        return ngettext(
            "You need at least one more conversation at level 1",
            "You need at least {n} level 1 conversations",
            n,
        ).format(n=n)


class ProfileLevel(LevelMixin, IntEnum):
    """
    PROFILE TRACK

    User gain points for filling in profile information.

    The test function receives an instance of Profile.
    """

    NONE = 0, _("No level")
    BASIC = 1, _("Basic")
    RELEVANT = 2, _("Relevant")
    INFORMATIVE = 3, _("Informative")
    COMPLETE = 4, _("Complete")

    @classmethod
    def check_level(cls, data):
        fields = set(PROFILE_EDITABLE_FIELDS)
        profile = get_profile(data.user)
        level = cls.NONE

        # First level: user completed the site tour.
        if True:
            level = cls.BASIC
        else:
            return level

        # Second level: user uploaded a photo.
        if profile.profile_photo and filled_gender_and_race(profile, fields):
            level = cls.RELEVANT
        else:
            return level

        # Third level: all one-liner fields.
        if filled_fields(profile, basic_profile_fields(fields)):
            level = cls.INFORMATIVE
        else:
            return level

        # Last level: user filled *ALL* profile info.
        if filled_gender_and_race(profile, fields) and filled_fields(profile, fields):
            level = cls.COMPLETE
        return level

    def achieve_next_level_msg(self, data):
        p = get_profile(data.user)
        fields = set(PROFILE_EDITABLE_FIELDS)

        if self == self.COMPLETE:
            return _("Congratulations! Your profile is complete!")

        elif self == self.NONE:
            return _("Please take the site tour!")

        elif self == self.BASIC:
            missing = []
            if "race" in fields and p.race == Race.NOT_FILLED:
                missing.append(_("race"))
            if "gender" in fields and p.gender == Gender.NOT_FILLED:
                missing.append(_("gender"))
            if not p.profile_photo:
                missing.append(_("profile photo"))
            if missing:
                return missing_fields_message(missing[:3])

        elif self == self.RELEVANT:
            fields_ = basic_profile_fields(fields)
            return missing_fields_message(missing_fields(p, fields_))

        elif self == self.INFORMATIVE:
            return missing_fields_message(missing_fields(p, fields))


# Helper functions


def filled_gender_and_race(p, fields):
    if "race" in fields and p.race == Race.NOT_FILLED:
        return False
    if "gender" in fields and p.gender == Gender.NOT_FILLED:
        return False
    return True


def filled_fields(profile, fields):
    is_filled = lambda f: f is not None and f != ""
    return all(is_filled(getattr(profile, f)) for f in fields)


def basic_profile_fields(fields):
    basic = {"gender", "race", "birth_date", "occupation", "city", "state", "country", "education"}
    return fields.intersection(basic)


def missing_fields(profile, fields):
    missing = []
    for field in fields:
        if getattr(profile, field, None) in (None, ""):
            missing.append(_(field.replace("_", " ")))
    return missing[:3]


def missing_fields_message(fields):
    data = fields[0] if len(fields) == 1 else humanize_list(fields)
    return ngettext(
        "Please fill up the {} field of your profile",
        "Please fill up the {} fields of your profile",
        len(fields),
    ).format(data)


def humanize_list(lst):
    if not lst:
        return ""
    lst = lst.copy()
    last = lst.pop()
    return __("{} and {}").format(", ".join(map(str, lst)), last)


# ==============================================================================
# Levels that consume ConversationProgress information
# ------------------------------------------------------------------------------


class ConversationLevel(LevelMixin, IntEnum):
    """
    CONVERSATION TRACK

    Track total participation in a conversation.

    The test function receives an instance of ConversationProgress.
    """

    NONE = 0, _("No level")
    ALIVE = 1, _("Alive")
    ENGAGING = 2, _("Engaging")
    NOTEWORTHY = 3, _("Noteworthy")
    DEBATE = 4, _("Debate")

    @staticmethod
    def _levels():
        return 50, 500, 5000, 50000

    @classmethod
    def check_level(cls, obj):
        result = cls.NONE
        for level, score in zip(cls.skipping_none(), cls._levels()):
            if obj.score >= score:
                result = level
            else:
                break
        return result

    def achieve_next_level_msg(self, obj):
        for level, score in zip(type(self), self._levels()):
            if score > obj.score:
                msg = _("Conversation needs a score of at least {n} points, it has {m}.")
                return msg.format(n=score, m=obj.score)
        return _("Conversation already achieved the maximum level.")


# ==============================================================================
# Levels that consume ParticipationProgresss information
# ------------------------------------------------------------------------------
VoterLevelConfig = namedtuple("VoterLevelConfig", ["votes", "ratio", "votes_sure"])


class VoterLevel(LevelMixin, IntEnum):
    """
    VOTER TRACK

    Keeps track of user participation on each conversation.

    The test function receives an instance of ParticipationProgress.
    """

    NONE = 0, _("No level")
    CURIOUS = 1, _("Curious")
    PARTICIPATIVE = 2, _("Participative")
    DEDICATED = 3, _("Dedicated")
    PERFECTIONIST = 4, _("Perfectionist")
    comment_bonus = property(lambda self: int(self))

    # Must be a staticmethod because we can't access values directly from the
    # class and if it was a simple list instance, it would become a valid enum
    # value, which we don't want.
    @staticmethod
    def _ranges():
        # m: minimum number of votes
        # r: minimum ratio between number of votes and number of comments
        # n: number of votes that yields level, even if r is not enough
        return (
            VoterLevelConfig(votes=5, ratio=0, votes_sure=10),
            VoterLevelConfig(votes=10, ratio=0.25, votes_sure=25),
            VoterLevelConfig(votes=25, ratio=0.50, votes_sure=75),
            VoterLevelConfig(votes=50, ratio=0.99, votes_sure=250),
        )

    @classmethod
    def check_level(cls, obj):
        result = cls.NONE
        votes = obj.n_final_votes
        ratio = obj.votes_ratio

        for level, (m, r, n) in zip(cls.skipping_none(), cls._ranges()):
            if votes < n and (votes < m or ratio < r):
                break
            else:
                result = level
        return result

    def achieve_next_level_msg(self, obj):
        # Special cases
        if self == self.PERFECTIONIST:
            return _("Congratulations! You already achieved the maximum participation level.")

        # Now we compute how many votes are necessary to progress
        votes = obj.n_final_votes
        m, r, n = self._ranges()[self]
        if votes == obj.n_conversation_comments:
            msg = _("You cannot progress unless conversation has at least {n} comments :-(")
            return msg.format(n=m)

        delta = float("inf")
        delta_ = ceil((r - obj.votes_ratio) * obj.n_conversation_comments)
        delta_ = max(delta_, m - votes)
        delta = min(delta_, delta)
        delta = min(delta, n - votes)
        return ngettext(
            "You are only one vote short of advancing to the next level!",
            "You need to cast {n} more votes to advance to the next level!",
            delta,
        ).format(n=delta)


class ScoreLevel(int):
    """
    A enum-like level integer
    """

    LEVEL_NAMES = (
        (5, _("Beginner")),
        (10, _("Intermediate")),
        (20, _("Participative")),
        (30, _("Professional")),
        (40, _("Master")),
    )

    def __str__(self):
        for max_lvl, name in self.LEVEL_NAMES:
            if max_lvl >= self:
                return str(name)
        return str(_("Ultimate Master"))

    @classmethod
    def check_level(cls, progress):
        """
        Compute level from score.
        """
        return cls.from_score(progress.score)

    @classmethod
    def from_score(cls, score):
        if score < 1000:
            return cls(score / 100)
        else:
            return cls(10 + sqrt((score - 1000) / 100))

    def score_value(self):
        if self <= 10:
            return self * 100
        return 1000 + 100 * (self - 10) ** 2

    def achieve_next_level_msg(self, progress):
        delta_score = ScoreLevel(self + 1).score_value() - progress.score
        return _("You need {n} more points to upgrade.").format(n=delta_score)
