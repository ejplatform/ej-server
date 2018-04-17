from unittest.mock import patch
from django.test import RequestFactory
from rest_framework.permissions import IsAdminUser
from ej.users.permissions import IsCurrentUserOrAdmin
from test_plus.test import TestCase
from ..api_views import UserViewSet
from ..models import User


class TestUserViewSet(TestCase):

    def fake_function(self):
        user = User()
        user.name = "storedUser"
        user.email = "storedUser@email.com"
        return user

    def setUp(self):
        self.viewSet = UserViewSet()
        self.viewSet.format_kwarg = "mock"

    @patch.object(UserViewSet, 'get_object', fake_function)
    def test_retrieve(self):
        user = User()
        user.name = "loggedUser"
        user.email = "loggedUser@email.com"

        factory = RequestFactory()
        request = factory.get('/fake-url')
        request.user = user

        self.viewSet.request = request

        # User Search criteria
        response = self.viewSet.retrieve(request)
        assert response.data['name'] == "storedUser"
        # required fields
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

        # Search for the logged user
        response = self.viewSet.retrieve(request,pk='me')
        assert response.data['name'] == "loggedUser"

    def test_get_permission(self):

        self.viewSet.action = 'list'
        permissions = self.viewSet.get_permissions()
        assert permissions[0].__class__ is IsAdminUser
        assert self.viewSet.permission_classes[0] == permissions[0].__class__

        self.viewSet.action = 'retrieve'
        permissions = self.viewSet.get_permissions()
        assert permissions[0].__class__ is IsCurrentUserOrAdmin
        assert self.viewSet.permission_classes[0] == permissions[0].__class__

        self.viewSet.action = None
        try:
            self.viewSet.get_permissions()
            assert False
        except ValueError:
            assert True




