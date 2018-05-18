from test_plus.test import TestCase

from ..permissions import IsCurrentUserOrAdmin


class TestIsCurrentUserOrAdmin(TestCase):

    def test_has_object_permission(self):
        class Mock(object):
            pass

        obj = Mock()
        request = Mock()
        request.user = Mock()
        request.user.is_superuser = True

        permission = IsCurrentUserOrAdmin()

        # superUser has permission
        assert permission.has_object_permission(request, obj) is True

        # Not a super user
        request.user.is_superuser = False
        # obj is not request.user
        assert permission.has_object_permission(request, obj) is False

        # obj is request.user
        obj.is_superuser = False
        request.user = obj
        assert permission.has_object_permission(request, obj) is True

        # No User passed
        request.user = None
        assert permission.has_object_permission(request, obj) is False
