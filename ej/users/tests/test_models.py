from test_plus.test import TestCase
from allauth.socialaccount.models import SocialAccount
from ..models import UserManager, User

class TestUser(TestCase):

    DEFAULT_USER_AVATAR = 'https://gravatar.com/avatar/7ec7606c46a14a7ef514d1f1f9038823?s=40&d=mm'

    def make_filled_user(self):
        filled_user = self.make_user('testfilleduser')
        filled_user.name = "name test" 
        filled_user.image = "image test"
        filled_user.age = 1
        filled_user.country = "country test"
        filled_user.city = "city test"
        filled_user.state = "state test"
        filled_user.biography = "biography test"
        filled_user.occupation = "occupation test"
        filled_user.gender = "OTHER"
        filled_user.political_movement = "political movement test"
        filled_user.race = "UNDECLARED"

        return filled_user

    def setUp(self):
        self.user = self.make_user()
        self.filled_user = self.make_filled_user()

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

    def test_image_url(self):
        
        #Test when user doesn't have a social account
        self.assertEqual(
            self.user.image_url,
            self.DEFAULT_USER_AVATAR
        )

        #@TO-DO test when exception
        #Test when user has a social account
        
        class Object(object):
            pass

        self.user.image = Object()
        self.user.image.url = None

        social_account = SocialAccount(self.user)

        
    def test_profile_filled(self):
        """
        By default a user is created partial filled.
        This method returns True when a user filled
        and False otherwise.
        """

        # Test partial filled user
        self.assertFalse(
            self.user.profile_filled
        )

        # Test filled user
        self.assertTrue(
            self.filled_user.profile_filled
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








