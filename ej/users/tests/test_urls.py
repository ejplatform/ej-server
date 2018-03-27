from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def test_list_reverse(self):
        """users:user-list should reverse to /api/profile/."""
        self.assertEqual(reverse('users:user-list'), '/api/profile/')

    def test_list_resolve(self):
        """/api/profile/ should resolve to users:user-list."""
        self.assertEqual(resolve('/api/profile/').view_name, 'users:user-list')

    def test_redirect_reverse(self):
        """users:redirect should reverse to /users/~redirect/."""
        self.assertEqual(reverse('users:redirect'), '/api/profile/~redirect/')

    def test_redirect_resolve(self):
        """/users/~redirect/ should resolve to users:redirect."""
        self.assertEqual(
            resolve('/api/profile/~redirect/').view_name,
            'users:redirect'
        )

    def test_detail_reverse(self):
        """users:user-detail should reverse to /api/profile/<pk>."""
        self.assertEqual(
            reverse('users:user-detail', kwargs={'pk': self.user.id}),
            '/api/profile/{}/'.format(self.user.id)
        )

    def test_detail_resolve(self):
        """/api/profile/<pk> should resolve to users:user-detail."""
        self.assertEqual(
            resolve('/api/profile/{}/'.format(self.user.id)).view_name,
            'users:user-detail'
        )

    def test_update_reverse(self):
        """users:update should reverse to /users/~update/."""
        self.assertEqual(reverse('users:update'), '/api/profile/~update/')

    def test_update_resolve(self):
        """/users/~update/ should resolve to users:update."""
        self.assertEqual(
            resolve('/api/profile/~update/').view_name,
            'users:update'
        )
