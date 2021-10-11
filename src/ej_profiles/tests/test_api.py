from ej_profiles.api import phone_number
import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from ej_boards.mommy_recipes import BoardRecipes
from ej_profiles.models import Profile

# BoardRecipes.update_globals(globals())

BASE_URL = "/api/v1"
PHONE_NUMBER = "61982734758"


class TestGetRoutesProfile(BoardRecipes):
    def test_phone_number_endpoint(self, mk_user):
        user = mk_user(email="someemail@domain.com")
        Profile.objects.create(user=user, phone_number=PHONE_NUMBER)
        token = Token.objects.create(user=user)
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        path = BASE_URL + f"/profiles/phone-number/"
        response = api.get(path)
        assert response.status_code == 200
        assert response.content.decode().strip('"') == PHONE_NUMBER

    def test_conversation_votes_endpoint_with_anonymous(self):
        api = APIClient()
        path = BASE_URL + f"/profiles/phone-number/"
        response = api.get(path)
        assert response.status_code == 403
