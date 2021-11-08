import pytest
import mock
from boogie.testing.pytest import ModelTester
from ej.testing import EjRecipes
from ej_users import password_reset_token
from ej_users.models import User, PasswordResetToken, clean_expired_tokens, MetaData, SignatureFactory
from ej_users.mommy_recipes import UserRecipes
from ej_conversations.mommy_recipes import ConversationRecipes


class TestUser(UserRecipes, ModelTester):
    model = User
    representation = "user@domain.com"


class TestUserManager(EjRecipes):
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user("name@server.com", "1234", name="name")
        assert user.name == "name"
        assert user.password != "1234"
        assert not user.is_superuser
        assert User.objects.get_by_email("name@server.com") == user

    def test_can_create_and_fetch_superuser(self, db):
        user = User.objects.create_superuser("name@server.com", "1234", name="name")
        assert user.name == "name"
        assert user.password != "1234"
        assert user.is_superuser
        assert User.objects.get_by_email("name@server.com") == user

        # Check unhappy paths
        with pytest.raises(ValueError):
            User.objects.create_superuser("name@server.com", "1234", is_superuser=False)
        with pytest.raises(ValueError):
            User.objects.create_superuser("name@server.com", "1234", is_staff=False)

    def test_generate_username(self):
        user = User(email="email@at.com")
        assert user.username == "email__at.com"


class TestPasswordResetToken(EjRecipes):
    def test_expiration(self, user):
        token = PasswordResetToken(user=user)
        assert not token.is_expired

    def test_password_reset_token(self, user):
        token = password_reset_token(user, commit=False)
        assert token.user == user
        assert token.url

    def test_clean_expired_tokens(self, user_db):
        token = password_reset_token(user_db)
        assert PasswordResetToken.objects.filter(user=user_db).exists()
        token.use()
        clean_expired_tokens()
        assert not PasswordResetToken.objects.filter(user=user_db).exists()


class TestMetaData(EjRecipes):
    def test_can_create_metadata(self, user_db):
        user = User.objects.create_user("name@server.com", "1234", name="name")
        metadata = MetaData.objects.create(analytics_id="GA.1.1234", mautic_id="9876", user=user)
        assert metadata
        assert user.metadata_set.first().id == metadata.id


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
