from test_plus.test import TestCase

from ej.configurations.models import SocialMediaIcon


class TestSocialMediaIcon(TestCase):

    def setUp(self):
        self.social_media_icon = SocialMediaIcon()
        self.social_media_icon.social_network = 'twitter'

    def test_str(self):
        self.assertEqual(
            str(self.social_media_icon),
            'twitter'
        )

    def test_html(self):
        self.assertEqual(
            self.social_media_icon.__html__(),
            '<a href=""><i  class="""></i></a>'
        )

    def test_icon_tag(self):
        self.assertEqual(
            self.social_media_icon.icon_tag(),
            '<i  class="""></i>'
        )