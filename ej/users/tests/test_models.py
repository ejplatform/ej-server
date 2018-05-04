from test_plus.test import TestCase
from unittest.mock import patch
from allauth.socialaccount.models import SocialAccount


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