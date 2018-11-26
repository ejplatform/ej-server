from boogie.testing.model import ModelTester
from ej.testing import EjRecipes
from ej_profiles.choices import Race, Gender
from ej_users import password_reset_token
from ej_users.models import User, PasswordResetToken, clean_expired_tokens
from ej_users.mommy_recipes import UserRecipes


class TestUser(UserRecipes, ModelTester):
    model = User
    representation = 'user@domain.com'


class TestUserManager(EjRecipes):
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user('name@server.com', '1234', name='name')
        assert user.name == 'name'
        assert user.password != '1234'
        assert User.objects.get_by_email('name@server.com') == user

    def test_generate_username(self):
        user = User(email='email@at.com')
        assert user.username == 'email__at.com'

    def test_user_profile_default_values(self, db):
        user = User.objects.create_user('email@at.com', 'pass')
        assert user.profile.gender == Gender.UNFILLED
        assert user.profile.race == Race.UNFILLED
        assert user.profile.age is None
        assert user.profile.gender_other == ''
        assert user.profile.country == ''
        assert user.profile.state == ''
        assert user.profile.city == ''
        assert user.profile.biography == ''
        assert user.profile.occupation == ''
        assert user.profile.political_activity == ''


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
