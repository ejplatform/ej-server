from pinax.badges.base import Badge, BadgeAwarded, BadgeDetail
from pinax.badges.registry import badges

from ej_conversations.models import Vote, Conversation


class UserCreatedBadge(Badge):
    slug = "user_created_badge"
    levels = [BadgeDetail("created", "Badge POVOQUER")]
    events = ["user_created"]

    multiple = False

    def award(self, **state):
        return BadgeAwarded(level=1)


class UserProfileFilledBadge(Badge):
    slug = "user_profile_created_badge"
    levels = [BadgeDetail("user_profile_filled", "User Profile Filled")]
    events = ["user_profile_filled"]
    multiple = False

    def award(self, **state):
        user = state["user"]
        if user.profile_filled:
            return BadgeAwarded(level=1)


class OpinionatorBadge(Badge):
    slug = "opinionator_badge"
    levels = [
        BadgeDetail("opinionator_first_three_votes", "User Voted First 3 Times"),
        BadgeDetail("opinionator_level_2", "User Voted 40 Times"),
        BadgeDetail("opinionator_level_3", "User Voted 80 Times"),
        BadgeDetail("opinionator_level_4", "User Voted 120 Times"),
    ]

    events = ["vote_cast"]
    multiple = False

    def award(self, **state):
        user = state["user"]
        vote_count = Vote.objects.filter(author=user).count()
        if vote_count >= 120:
            return BadgeAwarded(level=4)
        elif vote_count >= 80:
            return BadgeAwarded(level=3)
        elif vote_count >= 40:
            return BadgeAwarded(level=2)
        elif vote_count >= 3:
            return BadgeAwarded(level=1)


class KnowItAllBadge(Badge):
    slug = "know_it_all_badge"
    levels = [
        BadgeDetail("know_it_all_level_1", "Know-it-all Level 1"),
        BadgeDetail("know_it_all_level_2", "Know-it-all Level 2"),
        BadgeDetail("know_it_all_level_3", "Know-it-all level 3"),
        BadgeDetail("know_it_all_level_4", "Know-it-all level 4"),
        BadgeDetail("know_it_all_level_5", "Know-it-all level 5"),
        BadgeDetail("know_it_all_level_6", "Know-it-all level 6"),
        BadgeDetail("know_it_all_level_7", "Know-it-all level 7"),
        BadgeDetail("know_it_all_level_8", "Know-it-all level 8"),
        BadgeDetail("know_it_all_level_9", "Know-it-all level 9"),
        BadgeDetail("know_it_all_level_10", "Know-it-all level 10"),
        BadgeDetail("know_it_all_level_11", "Know-it-all level 11"),
        BadgeDetail("know_it_all_level_12", "Know-it-all level 12"),
        BadgeDetail("know_it_all_level_13", "Know-it-all level 13"),
        BadgeDetail("know_it_all_level_14", "Know-it-all level 14"),
        BadgeDetail("know_it_all_level_15", "Know-it-all level 15"),
        BadgeDetail("know_it_all_level_16", "Know-it-all level 16"),
        BadgeDetail("know_it_all_level_17", "Know-it-all level 17"),
        BadgeDetail("know_it_all_level_18", "Know-it-all level 18"),
        BadgeDetail("know_it_all_level_19", "Know-it-all level 19"),
        BadgeDetail("know_it_all_level_20", "Know-it-all level 20"),
    ]
    events = ["vote_cast"]
    multiple = False

    def award(self, **state):
        award_level = 0

        user = state["user"]
        votes_list = [
            Vote.objects.filter(comment__conversation=c, author=user).count()
            for c in Conversation.objects.all()
        ]

        # If the user has any number of votes in at least two conversations, give him the level 1
        if sum(i > 0 for i in votes_list) >= 2:
            award_level = 1

        # major_participations stores the number of conversations in wich the user voted 30 or more times
        major_participations = sum([i >= 30 for i in votes_list])
        award_level = award_level + major_participations

        # Ensure that you'll never award a level that is not set yet
        available_levels = len(KnowItAllBadge.levels)
        if award_level > available_levels:
            return BadgeAwarded(level=available_levels)

        return BadgeAwarded(level=award_level)


badges.register(UserCreatedBadge)
badges.register(UserProfileFilledBadge)
badges.register(OpinionatorBadge)
badges.register(KnowItAllBadge)
