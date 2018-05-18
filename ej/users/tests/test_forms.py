from test_plus.test import TestCase
from ..forms import EJSignupForm
from ..models import User
from django.test import RequestFactory
from unittest.mock import patch
from captcha.fields import ReCaptchaField


class TestEjSignupForm(TestCase):

    # Mock captch to be valid
    @patch.object(ReCaptchaField, 'clean', lambda x, y: y[0])
    def test_signup(self):
        data = {"full_name": "Rodrigo Oliveira"}
        form = EJSignupForm(data=data)
        user = User()
        user.username = "TestUsername"
        user.password = "pass1"
        user.email = "ej@ej.com"

        self.factory = RequestFactory()
        request = self.factory.get('/fake-url')

        assert(form.is_valid())

        form.signup(user)
        userFound = User.objects.filter(username="TestUsername").first()

        assert userFound.first_name == "Rodrigo"
        assert userFound.last_name == "Oliveira"
        assert userFound.email == "ej@ej.com"

    def test_captcha_is_valid(self):
        data = {"full_name": "Rodrigo Oliveira"}
        form = EJSignupForm(data)
        assert form.is_valid() is False
