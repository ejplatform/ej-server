from test_plus.test import TestCase
from ..models import UserManager, User

class TestUser(TestCase):

    def setUp(self):
        self.user = self.make_user()

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            'testuser'  # This is the default username for self.make_user()
        )

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(),
            '/api/v1/users/{}/'.format(self.user.id)
        )

class TestUserManager(TestCase):
    def setUp(self):
        self.user_manager = UserManager()
        self.user_manager.model = User
        self.user_manager.create_user(username="asd", email="fake@to.populate", password="abcd")
        self.user_manager.create_user(username="ej", email="empurrando@email.com", password="123")
        self.user_manager.create_user(username="asd2", email="fake2@to.populate", password="abcd")

    def test_get_by_email_or_username(self):
        #Find by username
        user = self.user_manager.get_by_email_or_username("ej")
        assert user.email == "empurrando@email.com"
        assert user.username == "ej"

        #Find by email
        user = self.user_manager.get_by_email_or_username("empurrando@email.com")
        assert user.username == "ej"
        assert user.email == "empurrando@email.com"

        #Raise error if not found
        try:
            self.user_manager.get_by_email_or_username("do not exist")
            assert False
        except:
            assert True

    def test_create_simple_user(self):
        user = self.user_manager.create_simple_user("ej2", "empurrando2@email.com", "123123")

        # Test user created
        assert user.__class__ == User
        assert user.name == "ej2"
        assert user.email == "empurrando2@email.com"
        assert self.user_manager.get_by_email_or_username("empurrando2@email.com") == user

        # Email that is already used should raise exception
        try:
            self.user_manager.create_simple_user("ej2", "empurrando2@email.com", "123123")
            assert False
        except:
            assert True

    def create_user(self, username):
        self.user_manager.create_user(username=username, email="empurrando2@email.com", password="abcd")

    def create_username(self, username):
        username = self.user_manager.available_username("empurrando juntos", "empurrando2@email.com")
        assert username == username
        self.create_user(username)

    def test_available_user_name(self):

        # Test Available Name combinations based on email and name
        #Email name
        self.create_user("empurrando2")

        #First name
        self.create_user("empurrando")

        #Last name
        self.create_user("juntos")

        #Last name + email domain
        self.create_user("juntos_email")

        #Emailname + email domain
        self.create_user("empurrando2_email")


        #Test username generation for emailname + numbers from 0 to 1000
        for i in range(1000):
            self.create_user("empurrando2_" + str(i))

        #After 1000 name should be random
        username = self.user_manager.available_username("empurrando juntos", "empurrando2@email.com")
        assert username != "empurrando2_1001"








