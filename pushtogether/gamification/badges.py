from pinax.badges.base import Badge, BadgeAwarded, BadgeDetail
from pinax.badges.registry import badges
from pushtogether.conversations.models import Vote
from pinax.points.models import AwardedPointValue

class UserCreatedBadge(Badge):
    slug = "user_created_badge"
    levels = [
        BadgeDetail("created", "Badge POVOQUER"),
    ]
    events = ["user_created",]

    multiple = False

    def award(self, **state):
        print('entrou no user created badge')
        return BadgeAwarded(level=1)


class UserProfileFilledBadge(Badge):
    slug = "user_profile_created_badge"
    levels = [
        BadgeDetail("user_profile_filled", "User Profile Filled"),
    ]
    events = ["user_profile_filled",]
    multiple = False

    def award(self, **state):
        print('entrou no user profile created badge')
        user = state["user"]
        if user.profile_filled:
            return BadgeAwarded(level=1)


class OpinionatorBadge(Badge):
    slug = "opinionator_badge"
    levels = [
        BadgeDetail("opinionator_first_three_votes", "User Voted First 3 Times"),
        BadgeDetail("opinionator_level_2", "User Voted 40 Times"),
        BadgeDetail("opinionator_level_3", "User Voted 80 Times"),
        BadgeDetail("opinionator_level_4", "User Voted 120 Times")
    ]

    events = ["vote_cast",]
    multiple = False

    def award(self, **state):
        print('Entrou no first three votes')
        user = state["user"]
        vote_count = Vote.objects.filter(author=user).count()
        if vote_count == 3:
            return BadgeAwarded(level=1)
        if vote_count == 40:
            return BadgeAwarded(level=2)
        if vote_count == 80:
            return BadgeAwarded(level=3)
        if vote_count == 120:
            return BadgeAwarded(level=4)


class KnowItAllBadge(Badge):
    slug = "know_it_all_badge"
    levels = [
        BadgeDetail("know_it_all_level_1", "Know-it-all Level 1"),
        BadgeDetail("know_it_all_level_2", "Know-it-all Level 2"),
        BadgeDetail("know_it_all_level_3", "Know-it-all level 3"),
        BadgeDetail("know_it_all_level_4", "Know-it-all level 4")
    ]
    # events


badges.register(UserCreatedBadge)
badges.register(UserProfileFilledBadge)
badges.register(OpinionatorBadge)
