from ej_users.models import User
from ej_profiles.choices import Race, Gender


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
        assert user.profile.gender == Gender.UNDECLARED
        assert user.profile.race == Race.UNDECLARED
        assert user.profile.age is None
        assert user.profile.gender_other == ''
        assert user.profile.country == ''
        assert user.profile.state == ''
        assert user.profile.city == ''
        assert user.profile.biography == ''
        assert user.profile.occupation == ''
        assert user.profile.political_activity == ''
