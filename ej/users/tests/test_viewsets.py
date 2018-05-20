from django.test import RequestFactory
from test_plus.test import TestCase
from rest_framework import permissions

from ..api_views import UserViewSet
from ..permissions import IsCurrentUserOrAdmin


class TestUserViewSet(TestCase):

    TEST_KEYS = [
        'id',
        'url',
        'image',
        'name',
        'email',
        'biography',
        'city',
        'state',
        'country',
        'username',
        'race',
        'gender',
        'occupation',
        'age',
        'political_movement',
        'is_superuser',
    ]

    def setUp(self):
        self.factory = RequestFactory()
        self.viewset = UserViewSet()

    def test_retrieve(self):
        request = self.factory.get('/users/me')
        request.user = self.make_user()
        self.viewset.request = request
        self.viewset.format_kwarg = None
        self.viewset.view = None

        # Test if condition of the method
        response = self.viewset.retrieve(request, 'me')
        self.assertEqual(response.status_code, 200)

        for test_key in self.TEST_KEYS:
            assert True if test_key in response.data.keys() else False

    def test_get_permissions(self):
        self.viewset.action = 'list'
        self.assertEqual(self.viewset.get_permissions()[0].__class__, permissions.IsAdminUser)

        self.viewset.action = 'retrieve'
        self.assertEqual(self.viewset.get_permissions()[0].__class__, IsCurrentUserOrAdmin)
