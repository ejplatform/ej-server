from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def test_list_reverse(self):
        """users:user-list should reverse to /api/v1/users/."""
        self.assertEqual(reverse('v1:user-list'), '/api/v1/users/')

    def test_list_resolve(self):
        """/api/v1/users/ should resolve to users:user-list."""
        self.assertEqual(resolve('/api/v1/users/').view_name, 'v1:user-list')

    def test_redirect_reverse(self):
        """users:redirect should reverse to /accounts/redirect/."""
        self.assertEqual(reverse('users:redirect'), '/accounts/redirect/')

    def test_redirect_resolve(self):
        """/accounts/redirect/ should resolve to users:redirect."""
        self.assertEqual(
            resolve('/accounts/redirect/').view_name,
            'users:redirect'
        )

    def test_detail_reverse(self):
        """users:user-detail should reverse to /api/v1/users/<pk>."""
        self.assertEqual(
            reverse('v1:user-detail', kwargs={'pk': self.user.id}),
            '/api/v1/users/{}/'.format(self.user.id)
        )

    def test_detail_resolve(self):
        """/api/v1/users/<pk> should resolve to users:user-detail."""
        self.assertEqual(
            resolve('/api/v1/users/{}/'.format(self.user.id)).view_name,
            'v1:user-detail'
        )

    def test_update_reverse(self):
        """users:update should reverse to /users/update/."""
        self.assertEqual(reverse('users:update'), '/accounts/update/')

    def test_update_resolve(self):
        """/accounts/update/ should resolve to users:update."""
        self.assertEqual(
            resolve('/accounts/update/').view_name,
            'users:update'
        )
