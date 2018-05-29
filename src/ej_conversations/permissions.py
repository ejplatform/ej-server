from rest_framework import permissions


class IsAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        has_perm = super().has_permission(request, view)
        if request.method in permissions.SAFE_METHODS:
            return has_perm
        else:
            return has_perm and request.user.is_staff
