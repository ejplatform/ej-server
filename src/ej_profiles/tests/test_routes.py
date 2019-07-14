import random as rd
import string as s
from datetime import datetime

import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.utils.six import BytesIO

from ej.testing import UrlTester
from ej_users.models import User


class TestRoutes(UrlTester):
    user_urls = ["/profile/", "/profile/edit/", "/profile/contributions/"]


def create_image(filename, size=(100, 100), image_mode="RGB", image_format="png"):
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.name = filename
    data.seek(0)
    return data


@pytest.fixture
def logged_client(db):
    user = User.objects.create_user("email@server.com", "password")
    client = Client()
    client.force_login(user)
    return client


class TestEditProfile:
    def test_user_logged_access_edit_profile(self, logged_client):
        resp = logged_client.get("/profile/edit/")
        assert resp.status_code == 200

    def test_user_logged_edit_profile_picture(self, logged_client):
        avatar = create_image("avatar.png")
        avatar_file = SimpleUploadedFile("front.png", avatar.getvalue())
        form_data = {"name": "Maurice", "profile_photo": avatar_file, "gender": 0, "race": 0}

        response = logged_client.post("/profile/edit/", form_data)
        assert response.status_code == 302 and response.url == "/profile/"
        user = User.objects.get(email="email@server.com")
        assert user.profile.profile_photo.name

    def test_user_logged_edit_profile_basic_info(self, logged_client):
        def rand_str(size):
            return "".join(rd.choices(s.ascii_lowercase, k=size))

        def gen_birth_date():
            return f"{rd.randint(1900, 2020)}-{rd.randint(1, 12)}-" f"{rd.randint(1, 28)}"

        inf_fields = [
            "name",
            "city",
            "occupation",
            "country",
            "ethnicity",
            "education",
            "political_activity",
            "biography",
            "state",
            "gender",
            "race",
            "birth_date",
        ]
        inf_values = [
            *[rand_str(15)] * 8,
            "DF",
            rd.choice(list(range(0, 3)) + [20]),
            rd.randint(0, 6),
            gen_birth_date(),
        ]
        form_data = {k: v for k, v in zip(inf_fields, inf_values)}

        response = logged_client.post("/profile/edit/", form_data)
        assert (
            response.status_code == 302 and response.url == "/profile/"
        ), f"Error found using post message {form_data}"
        user = User.objects.get(email="email@server.com")

        for attr in ["gender", "race"]:
            assert getattr(user.profile, attr).value == form_data[attr]
            inf_fields.remove(attr)
        assert user.profile.birth_date == datetime.strptime(form_data["birth_date"], "%Y-%m-%d").date()
        inf_fields.remove("birth_date")

        for attr in inf_fields:
            assert getattr(user.profile, attr) == form_data[attr], attr
