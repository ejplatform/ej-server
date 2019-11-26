import datetime

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from ej.testing.fixture_class import EjRecipes
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_gamification.models import CommentPromotion, GivenPower, GivenBridgePower, GivenMinorityPower

today = datetime.datetime.now(timezone.utc)
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)


class TestCommentPromotion(ConversationRecipes):
    def test_create_comment_promotion_model(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email="user@domain.com")
        mk_comment = conversation.create_comment
        comment = mk_comment(user, "comment", status="approved", check_limits=False)

        promotion = CommentPromotion(start=today, end=tomorrow, comment=comment, promoter=user)
        promotion.save()
        other = mk_user(email="other@domain.com")
        promotion.users.set([user, other])
        assert not promotion.is_expired
        promotion.recycle()
        promotion_exists = CommentPromotion.objects.filter(comment=comment, promoter=user).exists()
        assert promotion_exists

        promotion.end = yesterday
        assert promotion.is_expired
        promotion.recycle()
        promotion_still_exists = CommentPromotion.objects.filter(comment=comment, promoter=user).exists()
        assert not promotion_still_exists


class TestGivenPower:
    def test_use_power(self):
        power = GivenPower()
        with pytest.raises(NotImplementedError):
            power.use_power()


class GivenPowerAbstractTester(ConversationRecipes, EjRecipes):
    power = None

    def test_given_power(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        users = [mk_user(email="foo@a.com"), mk_user(email="foo@b.com")]
        power = self.power.objects.create(
            start=today, end=tomorrow, user=users[0], conversation=conversation
        )
        power.affected_users = users
        assert set(power.data["affected_users"]) == {user.id for user in users}
        assert all(user in power.affected_users for user in users)

    def test_use_power(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        users = [mk_user(email="foo@a.com"), mk_user(email="foo@b.com")]
        power = self.power.objects.create(
            start=today, end=tomorrow, user=users[0], conversation=conversation
        )
        power.affected_users = users
        mk_comment = conversation.create_comment
        comment = mk_comment(users[0], "promoted_comment", status="approved", check_limits=False)
        power.use_power(comment)
        assert CommentPromotion.objects.filter(comment=comment).exists()

    def test_use_power_validation_error(self, db, mk_conversation, mk_user, conversation):
        conversation1 = mk_conversation()
        user = mk_user(email="email@email.com")
        other_user = mk_user(email="email@otheremail.com")
        power = self.power.objects.create(start=today, end=tomorrow, user=user, conversation=conversation1)
        power.affected_users = [user, other_user]

        conversation2 = conversation
        conversation2.title = "title21"
        conversation2.author = user
        conversation2.save()
        mk_comment = conversation2.create_comment
        comment = mk_comment(user, "promoted_comment", status="approved", check_limits=False)
        with pytest.raises(ValidationError):
            power.use_power(comment)


class TestBridgePower(GivenPowerAbstractTester):
    power = GivenBridgePower


class TestGivenMinorityPower(GivenPowerAbstractTester):
    power = GivenMinorityPower
