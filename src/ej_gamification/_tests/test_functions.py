import datetime
import pytest
from django.utils import timezone

from ej_gamification.models import GivenBridgePower, GivenMinorityPower
from ej_gamification.functions import (promote_comment, is_promoted,
                                       clean_expired_promotions, give_bridge_power, give_minority_power)
from ej_conversations.mommy_recipes import ConversationRecipes


class TestPowerFuctions(ConversationRecipes):
    @pytest.fixture
    def create_comment(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(email='user@domain.com')
        mk_comment = conversation.create_comment
        comment = mk_comment(user, 'comment', status='approved', check_limits=False)
        yield comment
        comment.delete()
        conversation.delete()

    def test_promote_comment(self, create_comment, mk_user):
        comment = create_comment
        users = [mk_user(email='email@email.com'), mk_user(email='email@dot.com')]
        promoter = mk_user(email='promoter@email.com')
        promotion = promote_comment(comment=comment, author=promoter, users=users)
        assert not promotion.is_expired

    def test_is_promoted_true(self, create_comment, mk_user):
        comment = create_comment
        user = mk_user(email='email@email.com')
        promote_comment(comment=comment, author=user, users=[user])
        assert is_promoted(comment, user)

    def test_is_promoted_false(self, create_comment, mk_user):
        comment = create_comment
        user = mk_user(email='email@mail.com')
        assert not is_promoted(comment, user)

    def test_give_bridge_power(self, db, mk_user, mk_conversation):
        conversation = mk_conversation()
        user = mk_user(email='user@user.com')
        power = give_bridge_power(user, conversation, [user])
        assert power
        assert power.user == user
        assert power.conversation == conversation
        assert isinstance(power, GivenBridgePower)

    def test_give_minority_power(self, db, mk_user, mk_conversation):
        conversation = mk_conversation()
        user = mk_user(email='user@user.com')
        power = give_minority_power(user, conversation, [user])
        assert power
        assert power.user == user
        assert power.conversation == conversation
        assert isinstance(power, GivenMinorityPower)

    def test_clean_zero_expired_promotions(self, db):
        clean_expired_promotions()
        assert True

    def test_clean_all_expired_promotions(self, create_comment, mk_user):
        comment = create_comment
        user = mk_user(email='email@email.com')
        today = datetime.datetime.now(timezone.utc)
        yesterday = today - datetime.timedelta(days=1)
        promote_comment(comment=comment, author=user, users=[user], expires=yesterday)

        mk_comment = comment.conversation.create_comment
        comment2 = mk_comment(user, 'commen11t', status='approved', check_limits=False)
        promote_comment(comment=comment2, author=user, users=[user], expires=yesterday)
        clean_expired_promotions()
        assert True
