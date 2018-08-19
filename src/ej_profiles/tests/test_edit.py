import pytest
import string as s
import random as rd
from PIL import Image
from datetime import datetime
from django.test import Client
from django.utils.six import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

from ej_users.models import User


def create_image(filename, size=(100, 100), image_mode='RGB',
                 image_format='png'):
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.name = filename
    data.seek(0)
    return data


@pytest.fixture
def logged_client(db):
    user = User.objects.create_user('email@server.com', 'password')
    client = Client()
    client.force_login(user)
    return client


class TestEditProfile:
    def test_user_logged_access_profile_url(self, logged_client):
        # post without body with forced login works
        resp = logged_client.post('/login/')
        # redirect to profile page
        assert resp.url == '/profile/' and resp.status_code == 302

    def test_user_logged_access_edit_profile(self, logged_client):
        resp = logged_client.get('/profile/edit/')
        assert resp.status_code == 200

    def test_user_logged_edit_profile_picture(self, logged_client):
        avatar = create_image('avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        form_data = {'image': avatar_file, 'gender': 0, 'race': 0}

        response = logged_client.post('/profile/edit/', form_data)
        assert response.status_code == 302 and response.url == '/profile/'
        user = User.objects.get(email='email@server.com')
        assert user.profile.image.name

    def test_user_logged_edit_profile_basic_info(self, logged_client):
        def rand_str(size):
            return ''.join(rd.choices(s.ascii_lowercase, k=size))

        def gen_birth_date():
            return f'{rd.randint(1900, 2020)}-{rd.randint(1, 12)}-' \
                   f'{rd.randint(1, 28)}'

        inf_fields = ['city', 'state', 'country', 'ethnicity', 'education',
                      'political_activity', 'biography', 'occupation',
                      'gender', 'race', 'birth_date']
        inf_values = [*[rand_str(15)] * 8, rd.randint(0, 20), rd.randint(0, 6),
                      gen_birth_date()]
        form_data = {k: v for k, v in zip(inf_fields, inf_values)}

        response = logged_client.post('/profile/edit/', form_data)
        assert response.status_code == 302 and response.url == '/profile/'
        user = User.objects.get(email='email@server.com')

        for attr in ['gender', 'race']:
            assert getattr(user.profile, attr).value == form_data[attr]
            inf_fields.remove(attr)
        assert user.profile.birth_date == datetime.strptime(
            form_data['birth_date'], '%Y-%m-%d').date()
        inf_fields.remove('birth_date')
        assert all(map(lambda attr: getattr(
            user.profile, attr) == form_data[attr], inf_fields))

    def test_user_not_logged_dont_access_edit_profile(self):
        client = Client()
        resp = client.get('/profile/edit/')
        assert 'login' in resp.url
