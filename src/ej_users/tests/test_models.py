import pytest
from ej_users.models import User, Token
from ej_profiles.choices import Race, Gender


@pytest.fixture
def user(db):
    user = User.objects.create_user('name@server.com', '1234', name='name')
    user.save()
    return user


class TestUserManager:
    def test_can_create_and_fetch_simple_user(self, db):
        user = User.objects.create_user('name@server.com', '1234', name='name')
        assert user.name == 'name'
        assert user.password != '1234'
        assert User.objects.get_by_email('name@server.com') == user

    def test_generate_username(self, db):
        user = User.objects.create_user('email@at.com', 'pass')
        expected = 'email__at.com'
        assert user.username == expected

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


class TestTokenUser:
    def test_token_exists(self, db, user):
        token = Token(user=user)
        assert not token.url_token
        token.generate_token()
        token.save()
        assert token.url_token

    def test_token_is_not_expired(self, db, user):
        token = Token(user=user)
        token.save()
        assert not token.is_expired
