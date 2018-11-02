import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ej_configurations.models import SocialMediaIcon, Color, Fragment


class TestSocialMediaIcon:
    def test_convert_simple_icon_to_strings(self):
        icon = SocialMediaIcon(social_network='github')
        assert str(icon) == 'github'
        assert icon.__html__() == '<i class="fab fa-github"></i>'

    def test_convert_icon_with_url_to_strings(self):
        icon = SocialMediaIcon(social_network='github',
                               url='http://github.com/foo/bar/')
        assert str(icon) == 'github'
        assert str(icon.icon_tag()) == '<i class="fab fa-github"></i>'
        assert icon.__html__() == '<a href="http://github.com/foo/bar/"><i class="fab fa-github"></i></a>'


class TestColor:
    @pytest.fixture
    def color(self):
        return Color(name='red', hex_value='#FF0000')

    def test_color_representation(self, color):
        assert str(color) == 'red: #FF0000'

    def test_color_with_invalid_value(self, db):
        color = Color(name='invalid', hex_value='*')
        with pytest.raises(ValidationError):
            color.full_clean()

    def test_color_with_valid_value(self, db):
        color = Color(name='invalid', hex_value='#FF0000')
        color.full_clean()


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
        assert fragment.__html__() == '<div>content</div>'

        fragment.content = '<p>content</p>'
        assert fragment.__html__() == '<div><p>content</p></div>'

    def test_fragment_string_representation(self, fragment):
        assert str(fragment) == 'name'

    def test_locked_fragment_cannot_be_deleted(self, fragment_db):
        fragment_db.lock()
        with pytest.raises(IntegrityError):
            fragment_db.delete()
