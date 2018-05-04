from unittest.mock import patch

from allauth.account.adapter import get_adapter
from django.test import RequestFactory
from test_plus.test import TestCase

from ..serializers import RegistrationSerializer


class TestRegistrationSerializer(TestCase):

    def create_serializer(self):
        self.serializer = RegistrationSerializer(data="test serializer")
        self.serializer.is_valid()

    def test_get_cleaned_data(self):
        self.create_serializer()
        data = self.serializer.get_cleaned_data()

        assert "first_name" in data
        assert "last_name" in data
        assert "name" in data
        assert "tour_step" in data
        assert "username" in data
        assert "password1" in data
        assert "email" in data
        assert len(data) == 7

    @patch.object(get_adapter().__class__, 'save_user')
    def test_save(self, mocked_method):
        self.create_serializer()
        self.factory = RequestFactory()

        request = self.factory.get('/fake-url')
        request.session = {'account_verified_email': ''}

        # Serializer save method raises no exceptions
        try:
            user = self.serializer.save(request)
            assert True
        except:
            assert False

        # Function save_user should be called one time by the serializer instance.
        assert mocked_method.call_count == 1
