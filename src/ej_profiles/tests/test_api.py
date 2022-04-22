import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from ej_boards.mommy_recipes import BoardRecipes
from ej_profiles.models import Profile

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
        response_data = response.json()
        assert response_data.get("phone_number") == PHONE_NUMBER

    def test_set_phone_number_endpoint(self, mk_user):
        user = mk_user(email="someemail@domain.com")
        Profile.objects.create(user=user, phone_number=PHONE_NUMBER)
        token = Token.objects.create(user=user)
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        path = BASE_URL + f"/profiles/set-phone-number/"
        response = api.post(path, {"phone_number": "61981178174"})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data.get("phone_number") == "61981178174"

    def test_get_phone_number_endpoint_with_anonymous(self):
        api = APIClient()
        path = BASE_URL + f"/profiles/phone-number/"
        response = api.get(path)
        assert response.status_code == 401

    def test_set_phone_number_endpoint_with_anonymous(self):
        api = APIClient()
        path = BASE_URL + f"/profiles/set-phone-number/"
        response = api.post(path, {})
        assert response.status_code == 401
