from test_plus.test import TestCase
from allauth.socialaccount.models import SocialAccount
from ..models import UserManager, User


class TestUser(TestCase):

    DEFAULT_USER_AVATAR = 'https://gravatar.com/avatar/7ec7606c46a14a7ef514d1f1f9038823?s=40&d=mm'
    
    TEST_USER_NAME = 'name test'
    TEST_USER_EMAIL = 'testfilleduser@example.com'
    TEST_USER_IMAGE = 'image test'
    TEST_USER_AGE = 1
    TEST_USER_COUNTRY = 'country test'
    TEST_USER_CITY = 'city test'
    TEST_USER_STATE = 'state test'
    TEST_USER_BIOGRAPHY = 'biography test'
    TEST_USER_OCCUPATION = 'occupation test'
    TEST_USER_GENDER = 'Outro'
    TEST_USER_POLITICAL_MOVEMENT = 'political movement test'
    TEST_USER_RACE = 'Não declarado'

    def make_filled_user(self):
        filled_user = self.make_user('testfilleduser')
        filled_user.name = self.TEST_USER_NAME 
        filled_user.image = self.TEST_USER_IMAGE
        filled_user.age = self.TEST_USER_AGE
        filled_user.country = self.TEST_USER_COUNTRY
        filled_user.city = self.TEST_USER_CITY
        filled_user.state = self.TEST_USER_STATE
        filled_user.biography = self.TEST_USER_BIOGRAPHY
        filled_user.occupation = self.TEST_USER_OCCUPATION
        filled_user.gender = self.TEST_USER_GENDER
        filled_user.political_movement = self.TEST_USER_POLITICAL_MOVEMENT
        filled_user.race = self.TEST_USER_RACE

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
        The profile_filled method returns True when a user filled
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

    def test_get_profile_fields(self):
        """
        Return the fields (email, city, country, occupation,
        age, gender, race, political_movment, city) from user
        """
        test_user_fields = [
            self.TEST_USER_EMAIL,
            self.TEST_USER_CITY,
            self.TEST_USER_COUNTRY,
            self.TEST_USER_OCCUPATION,
            self.TEST_USER_AGE,
            self.TEST_USER_GENDER,
            self.TEST_USER_RACE,
            self.TEST_USER_POLITICAL_MOVEMENT,
        ]

        fields = self.filled_user.get_profile_fields()
        for field in fields:    
            assert True if field[1] in test_user_fields else False

    def test_get_profile_statistics(self):
        statistics = self.user.get_profile_statistics()
        self.assertTrue(statistics, {'votes': 0, 'comments': 0, 'conversations': 0})

    def test_get_role_description(self):
        self.assertTrue(self.user.get_role_description(), 'Regular user')
        
        self.user.is_staff = True
        self.assertTrue(self.user.get_role_description(), 'Administrative user')

        self.user.is_superuser = True
        self.assertTrue(self.user.get_role_description(), 'Root')


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








