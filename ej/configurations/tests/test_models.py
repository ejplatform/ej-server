import pytest
from django.db import IntegrityError
from markupsafe import Markup
from ej.configurations.models import SocialMediaIcon, Color, Fragment


class TestSocialMediaIcon:
    @pytest.fixture
    def social_media_icon(self):
        return SocialMediaIcon(
            social_network='social network'
        )

    def test_social_media_icon_string_representation(self, social_media_icon):
        assert str(social_media_icon) == 'social network'

    def test_social_media_icon_conversion_to_html(self, social_media_icon):
        assert social_media_icon.__html__() == '<a href=""><i  class="""></i></a>'

    def test_social_media_icon_html_tag(self, social_media_icon):
        assert social_media_icon.icon_tag() == '<i  class="""></i>'


class TestColor:
    @pytest.fixture
    def color(self):
        return Color(
            name='red',
            hex_value='#FF0000'
        )

    def test_color_representation(self, color):
        assert str(color) == 'red: #FF0000'


class TestFragment:
    @pytest.fixture
    def fragment(self):
        return Fragment(
            name='name',
            format='html',
            content='content'
        )

    @pytest.fixture
    def fragment_db(self, fragment, db):
        fragment.save()
        return fragment

    def test_fragment_conversion_to_html(self, fragment):
        assert fragment.__html__() == Markup('<div>content</div>')

        fragment.content = '<p>content</p>'
        assert fragment.__html__() == Markup('<div><p>content</p></div>')

    def test_fragment_string_representation(self, fragment):
        assert str(fragment) == 'name'

    def test_locked_fragment_cannot_be_deleted(self, fragment_db):
        fragment_db.lock()
        with pytest.raises(IntegrityError):
            fragment_db.delete()
