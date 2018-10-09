import datetime
from django.utils import timezone

from ej_powers.models import CommentPromotion  # GivenBridgePower, GivenMinorityPower
from ej_conversations.mommy_recipes import ConversationRecipes


today = datetime.datetime.now(timezone.utc)
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)


class TestCommentPromotion(ConversationRecipes):
    def test_create_comment_promotion_model(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email='user@domain.com')
        mk_comment = conversation.create_comment
        comment = mk_comment(user, 'comment', status='approved', check_limits=False)

        promotion = CommentPromotion(start=today, end=tomorrow, comment=comment, promoter=user)
        promotion.save()
        other = mk_user(email='other@domain.com')
        promotion.users.set([user, other])
        assert not promotion.is_expired

        promotion.end = yesterday
        assert promotion.is_expired
        promotion.recycle()
        promotion_still_exists = CommentPromotion.objects.filter(comment=comment, promoter=user).exists()
        assert not promotion_still_exists


class TestGivenBridgePower:
    def test_create_given_bridge_power_model(self):
        pass


class TestGivenMinorityPower:
    def test_given_minority_power(self):
        pass
