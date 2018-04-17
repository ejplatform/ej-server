from unittest.mock import patch
from django.test import RequestFactory

from test_plus.test import TestCase
from ..api_views import UserViewSet
from ..models import User

class TestUserViewSet(TestCase):
    def fake_function(self):
        user = User()
        user.name = "usuarioBuscado"
        user.email = "usuarioBuscado@arroba.com"
        return user

    @patch.object(UserViewSet, 'get_object', fake_function)
    def test_retrieve(self):
        user = User()
        user.name = "usuarioLogado"
        user.email = "usuarioLogado@arroba.com"

        factory = RequestFactory()
        request = factory.get('/fake-url')
        request.user = user

        viewSet = UserViewSet()
        viewSet.request = request
        viewSet.format_kwarg = "mock"

        # Busca de usuário
        response = viewSet.retrieve(request)
        assert response.data['name'] == "usuarioBuscado"
        assert 'email' in response.data
        assert 'biography' in response.data
        assert 'city' in response.data
        assert 'image' in response.data
        assert 'state' in response.data
        assert 'country' in response.data
        assert 'url' in response.data
        assert 'username' in response.data
        assert 'gender' in response.data
        assert 'race' in response.data
        assert 'tour_step' in response.data
        assert 'age' in response.data
        assert 'political_movement' in response.data
        assert 'is_superuser' in response.data
        assert 'id' in response.data
        assert len(response.data) == 17
        # Busca do usuário Logado
        response = viewSet.retrieve(request,pk='me')
        assert response.data['name'] == "usuarioLogado"





