import mock
import pytest
from ej_users.models import User
from ej_signatures.models import SignatureFactory
from ej_conversations.mommy_recipes import ConversationRecipes


class TestSignatureClass(ConversationRecipes):
    def test_user_get_default_signature(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        assert user.signature == "listen_to_community"

    def test_admin_can_add_conversation(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        signature = SignatureFactory.get_user_signature(admin_user)
        assert signature.can_add_conversation()

    def test_admin_can_vote(self, db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        signature = SignatureFactory.get_user_signature(admin_user)
        assert signature.can_vote()

    def test_community_signature_can_add_conversation(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        assert signature.can_add_conversation()

    def test_community_signature_can_vote(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        assert signature.can_vote()

    def test_community_signature_cannot_add_conversation_due_to_limit(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        signature.get_conversation_limit = mock.MagicMock(return_value=0)
        assert not signature.can_add_conversation()

    def test_community_signature_cannot_vote_due_to_limit(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        signature.get_vote_limit = mock.MagicMock(return_value=0)
        assert not signature.can_vote()

    def test_number_conversation_limit(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        assert signature.get_conversation_limit() == 20

    def test_number_vote_limit(self, db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        assert signature.get_vote_limit() == 100000

    def test_admin_can_access_wpp(self, conversation_db):
        admin_user = User.objects.create_superuser("admin@test.com", "pass")
        admin_user.save()
        signature = SignatureFactory.get_user_signature(admin_user)
        bot_tools = signature.get_tool("Opinion Bots", conversation_db)
        assert bot_tools.whatsapp.is_active

    def test_community_signature_regular_user_cannot_access_wpp(self, conversation_db, mk_user):
        user = mk_user(email="user@domain.com")
        signature = SignatureFactory.get_user_signature(user)
        bot_tools = signature.get_tool("Opinion Bots", conversation_db)
        assert not bot_tools.whatsapp.is_active
