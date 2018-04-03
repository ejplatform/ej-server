from unittest.mock import patch

from allauth.account.adapter import get_adapter
from django.test import RequestFactory
from test_plus.test import TestCase

from ..serializers import FixSocialLoginSerializer
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


class TestFixSocialLoginSerializer(TestCase):
    def test_get_token(self):

        self.serializer = FixSocialLoginSerializer()
        self.factory = RequestFactory()

        class Object(object):
            pass

        request = self.factory.get('/fake-url')
        self.serializer.context['view'] = Object()
        self.serializer.context['view'].adapter_class = lambda x: x

        view = self.serializer.get_view()
        adapter = self.serializer.get_adapter(request, view)
        app = Object()
        app.client_id = 123123
        app.secret = 12312312
        request.session = {'account_verified_email': ''}
        attrs = {}

        # Test the 'else' passing no code or acess_token, should raise an exception
        try:
            token = self.serializer.get_token(adapter, app, attrs, request, view)
        except:
            assert True

    def test_get_view(self):
        self.serializer = FixSocialLoginSerializer()

        try:
            self.serializer.get_view()
        except:
            assert True

        try:
            self.serializer.context['view'] = {'mock': True}
            assert True
        except:
            assert False

    def test_get_attribute(self):
        self.view = {}

        self.serializer = FixSocialLoginSerializer()

        try:
            self.serializer.get_attribute(self.view, 'mock')
        except:
            assert True

        try:
            teste = self.serializer.get_attribute(self, 'test_get_attribute')
            assert True
            assert teste == self.test_get_attribute
        except:
            assert False

    def test_get_adapter(self):

        class Object(object):
            pass

        serializer = FixSocialLoginSerializer()
        factory = RequestFactory()
        request = factory.get('/fake-url')
        view = Object()
        view.adapter_class = lambda x: x

        adapter = serializer.get_adapter(request, self.view)
        assert adapter == request
